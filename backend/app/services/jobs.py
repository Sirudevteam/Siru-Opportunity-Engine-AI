from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models import (
    AIReport,
    AuditScore,
    Campaign,
    CRMActivity,
    CRMStage,
    CrawlJob,
    JobStatus,
    Lead,
    MessageChannel,
    OutreachMessage,
    Proposal,
    Screenshot,
    Website,
    WebsiteAudit,
)
from app.schemas import Actor
from app.services.ai_engine import generate_ai_audit
from app.services.crawler import crawl_website
from app.services.google_places import discover_google_places
from app.services.leads import upsert_lead
from app.services.outreach import generate_outreach_messages
from app.services.pdf import build_audit_pdf, build_proposal_pdf
from app.services.scoring import SCORE_WEIGHTS, final_lead_score
from app.services.storage import ObjectStorage, storage_key
from app.services.vector_store import try_index_audit


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_job(
    db: Session,
    job_type: str,
    campaign_id: str | None = None,
    lead_id: str | None = None,
    result: dict | None = None,
) -> CrawlJob:
    job = CrawlJob(
        campaign_id=campaign_id,
        lead_id=lead_id,
        job_type=job_type,
        status=JobStatus.pending.value,
        progress_percent=0,
        current_step="Queued",
        result=result or {},
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_google_places_job(job_id: str, limit: int = 50) -> None:
    db = SessionLocal()
    try:
        job = db.get(CrawlJob, job_id)
        if not job or not job.campaign_id:
            return
        campaign = db.get(Campaign, job.campaign_id)
        if not campaign:
            fail_job(db, job, "Campaign not found.")
            return
        start_job(db, job, "Discovering Google Places leads")
        discovered = discover_google_places(campaign.country, campaign.city, campaign.industry, limit)
        update_job(db, job, 45, "Importing discovered leads")
        imported = 0
        duplicates = 0
        lead_ids: list[str] = []
        for payload in discovered:
            lead, created = upsert_lead(db, campaign, payload)
            if created:
                imported += 1
                lead_ids.append(lead.id)
            else:
                duplicates += 1
        complete_job(
            db,
            job,
            {"discovered": len(discovered), "imported": imported, "duplicates": duplicates, "lead_ids": lead_ids},
        )
    except Exception as exc:
        if "job" in locals() and job:
            fail_job(db, job, str(exc))
    finally:
        db.close()


def run_audit_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.get(CrawlJob, job_id)
        if not job or not job.lead_id:
            return
        lead = db.get(Lead, job.lead_id)
        if not lead:
            fail_job(db, job, "Lead not found.")
            return
        if not lead.website_url:
            fail_job(db, job, "Lead has no website URL.")
            return
        start_job(db, job, "Crawling website")
        crawl = crawl_website(lead.website_url)
        update_job(db, job, 45, "Saving website evidence")
        website_data = crawl.analysis["website_data"]
        website = Website(
            lead_id=lead.id,
            url=lead.website_url,
            final_url=website_data.get("final_url"),
            title=website_data.get("title"),
            meta_description=website_data.get("meta_description"),
            html_excerpt=website_data.get("html_excerpt"),
            headings=website_data.get("headings") or {},
            links=website_data.get("links") or {},
            images=website_data.get("images") or {},
            forms=website_data.get("forms") or {},
            cta_buttons=website_data.get("cta_buttons") or {},
            tech_stack=website_data.get("tech_stack") or {},
            raw_metrics=website_data.get("raw_metrics") or {},
        )
        db.add(website)
        db.flush()

        storage = ObjectStorage()
        for screenshot in crawl.screenshots:
            key = storage_key("screenshots", lead.id, f"{website.id}-{screenshot.viewport}.png")
            url = storage.save_bytes(key, screenshot.content, "image/png")
            db.add(
                Screenshot(
                    website_id=website.id,
                    viewport=screenshot.viewport,
                    storage_url=url,
                    width=screenshot.width,
                    height=screenshot.height,
                )
            )

        update_job(db, job, 65, "Scoring website")
        scoring = crawl.analysis["scoring"]
        audit = WebsiteAudit(
            lead_id=lead.id,
            website_id=website.id,
            total_score=scoring["total_score"],
            lead_priority=scoring["lead_priority"],
            problem_summary=scoring["problem_summary"],
            raw_checks=crawl.analysis["checks"],
        )
        db.add(audit)
        db.flush()
        for category, score in scoring["scores"].items():
            db.add(
                AuditScore(
                    audit_id=audit.id,
                    category=category,
                    score=score,
                    max_score=SCORE_WEIGHTS[category],
                    notes=None,
                )
            )

        lead.website_score = audit.total_score
        lead.priority_category = audit.lead_priority
        lead.final_lead_score = final_lead_score(
            lead.website_score,
            lead.business_value_score,
            lead.contactability_score,
            lead.industry_priority_score,
            lead.location_priority_score,
            lead.ai_closing_probability,
        )
        lead.crm_stage = CRMStage.audit_ready.value
        update_job(db, job, 85, "Indexing audit")
        try_index_audit(db, lead, audit)
        complete_job(db, job, {"website_id": website.id, "audit_id": audit.id, "score": audit.total_score})
    except Exception as exc:
        if "job" in locals() and job:
            fail_job(db, job, str(exc))
    finally:
        db.close()


def generate_ai_report(db: Session, lead: Lead, audit: WebsiteAudit) -> AIReport:
    settings = get_settings()
    campaign = db.get(Campaign, lead.campaign_id)
    currency = campaign.currency if campaign else settings.default_currency
    payload = generate_ai_audit(lead, audit, currency)
    report = AIReport(
        lead_id=lead.id,
        audit_id=audit.id,
        website_score=audit.total_score,
        problem_summary=payload["problem_summary"],
        business_risk=payload["business_risk"],
        improvement_opportunities=payload["improvement_opportunities"],
        recommended_service=payload["recommended_service"],
        estimated_project_value=payload["estimated_project_value"],
        outreach_angle=payload["outreach_angle"],
        closing_probability=payload["closing_probability"],
        raw_response=payload.get("raw_response", {}),
        prompt_version=payload.get("prompt_version", "audit-strategy-v1"),
        model_name=payload.get("model_name"),
        input_snapshot=payload.get("input_snapshot", {}),
        output_schema_version=payload.get("output_schema_version", "ai-report-v1"),
        token_usage=payload.get("token_usage", {}),
        cost_metadata=payload.get("cost_metadata", {}),
        failure_details=payload.get("failure_details", {}),
    )
    db.add(report)
    lead.ai_closing_probability = report.closing_probability
    lead.final_lead_score = final_lead_score(
        lead.website_score,
        lead.business_value_score,
        lead.contactability_score,
        lead.industry_priority_score,
        lead.location_priority_score,
        lead.ai_closing_probability,
    )
    db.commit()
    db.refresh(report)
    return report


def run_ai_report_job(job_id: str, audit_id: str | None = None) -> None:
    db = SessionLocal()
    try:
        job = db.get(CrawlJob, job_id)
        if not job or not job.lead_id:
            return
        lead = db.get(Lead, job.lead_id)
        audit = db.get(WebsiteAudit, audit_id) if audit_id else latest_audit(db, job.lead_id)
        if not lead or not audit:
            fail_job(db, job, "Lead or audit not found.")
            return
        start_job(db, job, "Generating AI report")
        report = generate_ai_report(db, lead, audit)
        complete_job(db, job, {"ai_report_id": report.id})
    except Exception as exc:
        if "job" in locals() and job:
            fail_job(db, job, str(exc))
    finally:
        db.close()


def run_outreach_job(job_id: str, channels: list[str] | None = None, actor_payload: dict | None = None) -> None:
    db = SessionLocal()
    try:
        job = db.get(CrawlJob, job_id)
        if not job or not job.lead_id:
            return
        lead = db.get(Lead, job.lead_id)
        if not lead:
            fail_job(db, job, "Lead not found.")
            return
        start_job(db, job, "Generating outreach drafts")
        selected = [
            MessageChannel(channel)
            for channel in (channels or [channel.value for channel in all_outreach_channels()])
        ]
        actor = Actor(**(actor_payload or {}))
        messages = create_outreach_drafts(db, lead, latest_ai_report(db, lead.id), selected, actor)
        complete_job(db, job, {"message_ids": [message.id for message in messages]})
    except Exception as exc:
        if "job" in locals() and job:
            fail_job(db, job, str(exc))
    finally:
        db.close()


def run_proposal_job(job_id: str, actor_payload: dict | None = None) -> None:
    db = SessionLocal()
    try:
        job = db.get(CrawlJob, job_id)
        if not job or not job.lead_id:
            return
        lead = db.get(Lead, job.lead_id)
        if not lead:
            fail_job(db, job, "Lead not found.")
            return
        start_job(db, job, "Generating proposal")
        proposal = create_proposal(db, lead, latest_ai_report(db, lead.id), Actor(**(actor_payload or {})))
        complete_job(db, job, {"proposal_id": proposal.id, "pdf_url": proposal.pdf_url})
    except Exception as exc:
        if "job" in locals() and job:
            fail_job(db, job, str(exc))
    finally:
        db.close()


def create_outreach_drafts(db: Session, lead: Lead, ai_report: AIReport | None, channels, actor: Actor):
    payloads = generate_outreach_messages(lead, ai_report, channels)
    messages = [
        OutreachMessage(
            lead_id=lead.id,
            ai_report_id=ai_report.id if ai_report else None,
            channel=payload["channel"].value,
            subject=payload["subject"],
            body=payload["body"],
            created_by_id=actor.id,
            created_by_name=actor.name,
        )
        for payload in payloads
    ]
    db.add_all(messages)
    db.commit()
    for message in messages:
        db.refresh(message)
    return messages


def create_proposal(db: Session, lead: Lead, ai_report: AIReport | None, actor: Actor) -> Proposal:
    campaign = db.get(Campaign, lead.campaign_id)
    currency = campaign.currency if campaign else get_settings().default_currency
    service = ai_report.recommended_service if ai_report else "Website Redesign + Local SEO"
    value = ai_report.estimated_project_value if ai_report else f"{currency} 75,000 - {currency} 250,000"
    proposal = Proposal(
        lead_id=lead.id,
        ai_report_id=ai_report.id if ai_report else None,
        title=f"{service} Proposal for {lead.business_name}",
        summary=(
            f"Siru recommends {service} for {lead.business_name}, focused on improving "
            "mobile experience, local SEO visibility, trust signals, and enquiry conversion."
        ),
        estimated_value=value,
        currency=currency,
        content={
            "sections": [
                {"title": "Business Context", "body": f"{lead.business_name} can improve website conversion."},
                {"title": "Recommended Approach", "body": service},
                {"title": "Expected Outcome", "body": "More qualified local enquiries and clearer trust signals."},
            ],
            "packages": [
                {"name": "Core", "price": value, "items": ["UX refresh", "Local SEO foundation"]},
            ],
            "timeline": "2-6 weeks depending on final scope.",
            "assumptions": ["Manual approval before sending.", "Final pricing depends on discovery."],
            "recommended_work": [
                "Website UX and mobile redesign",
                "Local SEO foundation",
                "Conversion-focused CTA and contact flow",
                "Trust signal and content improvements",
            ],
            "manual_send_only": True,
        },
        created_by_id=actor.id,
        created_by_name=actor.name,
    )
    db.add(proposal)
    db.flush()
    pdf_bytes = build_proposal_pdf(proposal, lead)
    key = storage_key("proposals", lead.id, f"{proposal.id}.pdf")
    proposal.pdf_url = ObjectStorage().save_bytes(key, pdf_bytes, "application/pdf")
    db.commit()
    db.refresh(proposal)
    return proposal


def latest_audit(db: Session, lead_id: str) -> WebsiteAudit | None:
    return (
        db.execute(
            select(WebsiteAudit)
            .where(WebsiteAudit.lead_id == lead_id)
            .options(joinedload(WebsiteAudit.scores))
            .order_by(WebsiteAudit.created_at.desc())
        )
        .unique()
        .scalars()
        .first()
    )


def latest_ai_report(db: Session, lead_id: str) -> AIReport | None:
    return db.scalar(
        select(AIReport).where(AIReport.lead_id == lead_id).order_by(AIReport.created_at.desc())
    )


def latest_website(db: Session, lead_id: str) -> Website | None:
    return (
        db.execute(
            select(Website)
            .where(Website.lead_id == lead_id)
            .options(joinedload(Website.screenshots))
            .order_by(Website.created_at.desc())
        )
        .unique()
        .scalars()
        .first()
    )


def all_outreach_channels() -> list[MessageChannel]:
    return [
        MessageChannel.email,
        MessageChannel.whatsapp,
        MessageChannel.linkedin,
        MessageChannel.follow_up,
        MessageChannel.call_script,
        MessageChannel.proposal_summary,
    ]


def add_activity(
    db: Session,
    lead: Lead,
    activity_type: str,
    note: str,
    actor: Actor,
    from_stage: str | None = None,
    to_stage: str | None = None,
    next_follow_up_at=None,
) -> CRMActivity:
    activity = CRMActivity(
        lead_id=lead.id,
        activity_type=activity_type,
        note=note,
        from_stage=from_stage,
        to_stage=to_stage,
        actor_id=actor.id,
        actor_name=actor.name,
        actor_role=actor.role,
        next_follow_up_at=next_follow_up_at,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def start_job(db: Session, job: CrawlJob, current_step: str = "Running") -> None:
    job.status = JobStatus.running.value
    job.progress_percent = max(job.progress_percent or 0, 5)
    job.current_step = current_step
    job.started_at = utcnow()
    db.commit()


def update_job(db: Session, job: CrawlJob, progress_percent: int, current_step: str) -> None:
    job.progress_percent = progress_percent
    job.current_step = current_step
    db.commit()


def complete_job(db: Session, job: CrawlJob, result: dict) -> None:
    job.status = JobStatus.completed.value
    job.progress_percent = 100
    job.current_step = "Completed"
    job.result = result
    job.completed_at = utcnow()
    db.commit()


def fail_job(db: Session, job: CrawlJob, error: str) -> None:
    job.status = JobStatus.failed.value
    job.error = error
    job.current_step = "Failed"
    job.completed_at = utcnow()
    db.commit()
