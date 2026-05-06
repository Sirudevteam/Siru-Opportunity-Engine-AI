from celery import Celery
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models import Lead, WebsiteAudit
from app.schemas import Actor
from app.services.jobs import (
    all_outreach_channels,
    create_outreach_drafts,
    create_proposal,
    generate_ai_report as generate_ai_report_service,
    latest_ai_report,
    run_audit_job,
    run_google_places_job,
)

settings = get_settings()

celery_app = Celery(
    "siru_opportunity_engine",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


@celery_app.task(name="discover_google_places")
def discover_google_places_task(job_id: str, limit: int = 50) -> None:
    run_google_places_job(job_id, limit)


@celery_app.task(name="crawl_website")
def crawl_website_task(job_id: str) -> None:
    run_audit_job(job_id)


@celery_app.task(name="analyze_website")
def analyze_website_task(job_id: str) -> None:
    run_audit_job(job_id)


@celery_app.task(name="generate_ai_report")
def generate_ai_report_task(lead_id: str, audit_id: str) -> str | None:
    db: Session = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        audit = db.get(WebsiteAudit, audit_id)
        if not lead or not audit:
            return None
        report = generate_ai_report_service(db, lead, audit)
        return report.id
    finally:
        db.close()


@celery_app.task(name="generate_outreach")
def generate_outreach_task(lead_id: str) -> list[str]:
    db: Session = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if not lead:
            return []
        report = latest_ai_report(db, lead_id)
        messages = create_outreach_drafts(db, lead, report, all_outreach_channels(), Actor())
        return [message.id for message in messages]
    finally:
        db.close()


@celery_app.task(name="generate_pdf")
def generate_pdf_task(lead_id: str) -> str | None:
    db: Session = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if not lead:
            return None
        proposal = create_proposal(db, lead, latest_ai_report(db, lead_id), Actor())
        return proposal.id
    finally:
        db.close()
