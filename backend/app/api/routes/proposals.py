from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_actor, require_role
from app.db.session import get_db
from app.models import Lead, Proposal
from app.schemas import Actor, JobRead, ProposalRead, ProposalUpdate
from app.services.jobs import create_job
from app.services.pdf import build_proposal_pdf
from app.services.storage import ObjectStorage, storage_key
from app.workers.celery_app import generate_pdf_task

router = APIRouter()


@router.get("", response_model=list[ProposalRead])
def list_proposals(
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> list[Proposal]:
    return list(db.scalars(select(Proposal).order_by(Proposal.created_at.desc())).all())


@router.post("/leads/{lead_id}/generate", response_model=JobRead)
def generate_proposal(
    lead_id: str,
    actor: Actor = Depends(get_actor),
    db: Session = Depends(get_db),
    _role=Depends(require_role("operate")),
) -> object:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    job = create_job(db, job_type="generate_proposal", campaign_id=lead.campaign_id, lead_id=lead.id)
    generate_pdf_task.delay(job.id, actor.model_dump())
    return job


@router.get("/{proposal_id}", response_model=ProposalRead)
def get_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> Proposal:
    proposal = db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return proposal


@router.patch("/{proposal_id}", response_model=ProposalRead)
def update_proposal(
    proposal_id: str,
    payload: ProposalUpdate,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("operate")),
) -> Proposal:
    proposal = db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(proposal, key, value)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.post("/{proposal_id}/approve", response_model=ProposalRead)
def approve_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("manage")),
) -> Proposal:
    proposal = db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    proposal.status = "approved"
    proposal.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.post("/{proposal_id}/archive", response_model=ProposalRead)
def archive_proposal(
    proposal_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("operate")),
) -> Proposal:
    proposal = db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    proposal.status = "archived"
    proposal.archived_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.post("/{proposal_id}/regenerate-pdf", response_model=ProposalRead)
def regenerate_proposal_pdf(
    proposal_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("operate")),
) -> Proposal:
    proposal = db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    lead = db.get(Lead, proposal.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    pdf_bytes = build_proposal_pdf(proposal, lead)
    key = storage_key("proposals", lead.id, f"{proposal.id}.pdf")
    proposal.pdf_url = ObjectStorage().save_bytes(key, pdf_bytes, "application/pdf")
    db.commit()
    db.refresh(proposal)
    return proposal
