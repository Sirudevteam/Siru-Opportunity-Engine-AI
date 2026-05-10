from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models import Campaign, CRMActivity, CrawlJob, EnrichmentRecord, Lead, OutreachMessage, Proposal
from app.schemas import (
    CSVImportSummary,
    GooglePlacesDiscoveryRequest,
    JobRead,
    LeadAuditDetail,
    LeadCreate,
    LeadRead,
    LeadUpdate,
)
from app.services.jobs import create_job, latest_ai_report, latest_audit, latest_website
from app.services.leads import import_csv_leads, upsert_lead
from app.services.normalization import (
    build_dedupe_key,
    business_value_score,
    contactability_score,
    extract_domain,
    normalize_email,
    normalize_phone,
    normalize_url,
)
from app.workers.celery_app import discover_google_places_task

router = APIRouter()


@router.get("", response_model=list[LeadRead])
def list_leads(
    campaign_id: str | None = None,
    crm_stage: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> list[Lead]:
    query = select(Lead).order_by(Lead.created_at.desc()).limit(limit)
    if campaign_id:
        query = query.where(Lead.campaign_id == campaign_id)
    if crm_stage:
        query = query.where(Lead.crm_stage == crm_stage)
    if priority:
        query = query.where(Lead.priority_category == priority)
    if search:
        like = f"%{search}%"
        query = query.where(Lead.business_name.ilike(like))
    return list(db.scalars(query).all())


@router.post("", response_model=LeadRead)
def create_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("operate")),
) -> Lead:
    campaign = db.get(Campaign, payload.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    lead, created = upsert_lead(db, campaign, payload.model_dump())
    db.commit()
    db.refresh(lead)
    if not created:
        raise HTTPException(status_code=409, detail="Duplicate lead already exists.")
    return lead


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> Lead:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return lead


@router.get("/{lead_id}/detail", response_model=LeadAuditDetail)
def get_lead_detail(
    lead_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> dict:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return {
        "lead": lead,
        "campaign": lead.campaign,
        "website": latest_website(db, lead_id),
        "audit": latest_audit(db, lead_id),
        "ai_report": latest_ai_report(db, lead_id),
        "outreach_messages": list(
            db.scalars(
                select(OutreachMessage)
                .where(OutreachMessage.lead_id == lead_id)
                .order_by(OutreachMessage.created_at.desc())
            ).all()
        ),
        "proposals": list(
            db.scalars(
                select(Proposal).where(Proposal.lead_id == lead_id).order_by(Proposal.created_at.desc())
            ).all()
        ),
        "crm_activities": list(
            db.scalars(
                select(CRMActivity)
                .where(CRMActivity.lead_id == lead_id)
                .order_by(CRMActivity.created_at.desc())
            ).all()
        ),
        "jobs": list(
            db.scalars(select(CrawlJob).where(CrawlJob.lead_id == lead_id).order_by(CrawlJob.created_at.desc())).all()
        ),
        "enrichments": list(
            db.scalars(
                select(EnrichmentRecord)
                .where(EnrichmentRecord.lead_id == lead_id)
                .order_by(EnrichmentRecord.created_at.desc())
            ).all()
        ),
    }


@router.patch("/{lead_id}", response_model=LeadRead)
def update_lead(
    lead_id: str,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("operate")),
) -> Lead:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(lead, key, value.value if hasattr(value, "value") else value)
    if any(key in updates for key in ["business_name", "website_url", "email", "phone", "city", "country"]):
        lead.website_url = normalize_url(lead.website_url)
        lead.email = normalize_email(lead.email)
        lead.phone = normalize_phone(lead.phone)
        lead.normalized_domain = extract_domain(lead.website_url)
        lead.dedupe_key = build_dedupe_key(
            lead.business_name, lead.website_url, lead.email, lead.phone, lead.city, lead.country
        )
        lead.contactability_score = contactability_score(lead.email, lead.phone, lead.website_url)
        lead.business_value_score = business_value_score(lead.google_rating, lead.review_count)
    db.commit()
    db.refresh(lead)
    return lead


@router.post("/import", response_model=CSVImportSummary)
async def import_leads(
    campaign_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _actor=Depends(require_role("operate")),
) -> dict:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    content = await file.read()
    return import_csv_leads(db, campaign, content)


@router.post("/discover/google-places", response_model=JobRead)
def discover_google_places_for_campaign(
    payload: GooglePlacesDiscoveryRequest,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("operate")),
) -> object:
    campaign = db.get(Campaign, payload.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    job = create_job(
        db,
        job_type="discover_google_places",
        campaign_id=campaign.id,
        result={"limit": payload.limit},
    )
    discover_google_places_task.delay(job.id, payload.limit)
    return job

