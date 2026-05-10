from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_actor, require_role
from app.db.session import get_db
from app.models import Lead, OutreachMessage
from app.schemas import Actor, JobRead, OutreachGenerateRequest, OutreachMessageRead
from app.services.jobs import create_job
from app.workers.celery_app import generate_outreach_task

router = APIRouter()


@router.post("/leads/{lead_id}/generate", response_model=JobRead)
def generate_outreach(
    lead_id: str,
    payload: OutreachGenerateRequest,
    actor: Actor = Depends(get_actor),
    db: Session = Depends(get_db),
    _role=Depends(require_role("operate")),
) -> object:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    job = create_job(db, job_type="generate_outreach", campaign_id=lead.campaign_id, lead_id=lead.id)
    generate_outreach_task.delay(job.id, [channel.value for channel in payload.channels], actor.model_dump())
    return job


@router.get("/leads/{lead_id}", response_model=list[OutreachMessageRead])
def list_outreach(
    lead_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> list[OutreachMessage]:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return list(
        db.scalars(
            select(OutreachMessage)
            .where(OutreachMessage.lead_id == lead_id)
            .order_by(OutreachMessage.created_at.desc())
        ).all()
    )

