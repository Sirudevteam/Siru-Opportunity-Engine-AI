from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_actor
from app.db.session import get_db
from app.models import CRMStage, Lead
from app.schemas import Actor, CRMActivityCreate, CRMActivityRead, CRMStageUpdate, PipelineColumn
from app.services.jobs import add_activity

router = APIRouter()


@router.get("/pipeline", response_model=list[PipelineColumn])
def get_pipeline(db: Session = Depends(get_db)) -> list[dict]:
    columns = []
    for stage in CRMStage:
        leads = list(
            db.scalars(
                select(Lead).where(Lead.crm_stage == stage.value).order_by(Lead.updated_at.desc())
            ).all()
        )
        columns.append(
            {
                "stage": stage,
                "leads": leads,
                "count": len(leads),
                "total_score": sum(lead.final_lead_score or 0 for lead in leads),
            }
        )
    return columns


@router.post("/leads/{lead_id}/stage", response_model=CRMActivityRead)
def move_stage(
    lead_id: str,
    payload: CRMStageUpdate,
    actor: Actor = Depends(get_actor),
    db: Session = Depends(get_db),
) -> object:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    from_stage = lead.crm_stage
    lead.crm_stage = payload.stage.value
    note = payload.note or f"Moved from {from_stage} to {payload.stage.value}."
    activity = add_activity(db, lead, "stage_change", note, actor, from_stage, payload.stage.value)
    return activity


@router.post("/leads/{lead_id}/activities", response_model=CRMActivityRead)
def create_activity(
    lead_id: str,
    payload: CRMActivityCreate,
    actor: Actor = Depends(get_actor),
    db: Session = Depends(get_db),
) -> object:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return add_activity(db, lead, payload.activity_type, payload.note, actor)

