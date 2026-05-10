from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models import CrawlJob, Lead, WebsiteAudit
from app.schemas import AuditRunResponse, JobRead, LeadAuditDetail
from app.services.jobs import (
    create_job,
    latest_ai_report,
    latest_audit,
    latest_website,
    run_audit_job,
)
from app.workers.celery_app import crawl_website_task, generate_ai_report_task

router = APIRouter()


@router.post("/leads/{lead_id}/run", response_model=AuditRunResponse)
def run_audit_for_lead(
    lead_id: str,
    inline: bool = Query(default=False),
    db: Session = Depends(get_db),
    _actor=Depends(require_role("operate")),
) -> dict:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    if not lead.website_url:
        raise HTTPException(status_code=422, detail="Lead has no website URL.")
    job = create_job(db, job_type="crawl_website", campaign_id=lead.campaign_id, lead_id=lead.id)
    if inline:
        run_audit_job(job.id)
        db.refresh(job)
    else:
        crawl_website_task.delay(job.id)
    return {"job": job, "message": "Audit job created."}


@router.get("/jobs/{job_id}", response_model=JobRead)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> CrawlJob:
    job = db.get(CrawlJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.get("/leads/{lead_id}", response_model=LeadAuditDetail)
def get_lead_audit(
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
    }


@router.post("/{audit_id}/ai-report", response_model=JobRead)
def create_ai_report(
    audit_id: str,
    inline: bool = Query(default=False),
    db: Session = Depends(get_db),
    _actor=Depends(require_role("operate")),
) -> object:
    audit = db.get(WebsiteAudit, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found.")
    lead = db.get(Lead, audit.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    job = create_job(db, job_type="generate_ai_report", campaign_id=lead.campaign_id, lead_id=lead.id)
    if inline:
        from app.services.jobs import run_ai_report_job

        run_ai_report_job(job.id, audit.id)
        db.refresh(job)
    else:
        generate_ai_report_task.delay(job.id, audit.id)
    return job

