from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_actor
from app.db.session import get_db
from app.models import Lead, Proposal
from app.schemas import Actor, ProposalRead
from app.services.jobs import create_proposal, latest_ai_report

router = APIRouter()


@router.get("", response_model=list[ProposalRead])
def list_proposals(db: Session = Depends(get_db)) -> list[Proposal]:
    return list(db.scalars(select(Proposal).order_by(Proposal.created_at.desc())).all())


@router.post("/leads/{lead_id}/generate", response_model=ProposalRead)
def generate_proposal(
    lead_id: str,
    actor: Actor = Depends(get_actor),
    db: Session = Depends(get_db),
) -> Proposal:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return create_proposal(db, lead, latest_ai_report(db, lead_id), actor)


@router.get("/{proposal_id}", response_model=ProposalRead)
def get_proposal(proposal_id: str, db: Session = Depends(get_db)) -> Proposal:
    proposal = db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return proposal
