from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_actor
from app.db.session import get_db
from app.models import Lead, OutreachMessage
from app.schemas import Actor, OutreachGenerateRequest, OutreachMessageRead
from app.services.jobs import create_outreach_drafts, latest_ai_report

router = APIRouter()


@router.post("/leads/{lead_id}/generate", response_model=list[OutreachMessageRead])
def generate_outreach(
    lead_id: str,
    payload: OutreachGenerateRequest,
    actor: Actor = Depends(get_actor),
    db: Session = Depends(get_db),
) -> list[OutreachMessage]:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return create_outreach_drafts(db, lead, latest_ai_report(db, lead_id), payload.channels, actor)


@router.get("/leads/{lead_id}", response_model=list[OutreachMessageRead])
def list_outreach(lead_id: str, db: Session = Depends(get_db)) -> list[OutreachMessage]:
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

