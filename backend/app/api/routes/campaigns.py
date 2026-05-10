from __future__ import annotations

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models import Campaign, CRMStage, CrawlJob, Lead
from app.schemas import CampaignCreate, CampaignDetail, CampaignRead, CampaignStatusUpdate, CampaignUpdate

from fastapi import APIRouter

router = APIRouter()


@router.get("", response_model=list[CampaignRead])
def list_campaigns(
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = None,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> list[Campaign]:
    query = select(Campaign).order_by(Campaign.created_at.desc())
    if status_filter:
        query = query.where(Campaign.status == status_filter)
    if search:
        like = f"%{search}%"
        query = query.where(Campaign.name.ilike(like))
    return list(db.scalars(query).all())


@router.post("", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("manage")),
) -> Campaign:
    campaign = Campaign(**payload.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return campaign


@router.get("/{campaign_id}/detail", response_model=CampaignDetail)
def get_campaign_detail(
    campaign_id: str,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("read")),
) -> dict:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    leads = list(
        db.scalars(select(Lead).where(Lead.campaign_id == campaign_id).order_by(Lead.created_at.desc())).all()
    )
    jobs = list(
        db.scalars(
            select(CrawlJob).where(CrawlJob.campaign_id == campaign_id).order_by(CrawlJob.created_at.desc())
        ).all()
    )
    stage_counts = {stage.value: 0 for stage in CRMStage}
    for lead in leads:
        stage_counts[str(lead.crm_stage)] = stage_counts.get(str(lead.crm_stage), 0) + 1
    audited = sum(1 for lead in leads if lead.website_score is not None)
    source_counts: dict[str, int] = {}
    owner_counts: dict[str, int] = {}
    for lead in leads:
        source_counts[lead.source] = source_counts.get(lead.source, 0) + 1
        owner = lead.owner_name or "Unassigned"
        owner_counts[owner] = owner_counts.get(owner, 0) + 1
    return {
        "campaign": campaign,
        "metrics": {
            "total_leads": len(leads),
            "audited_leads": audited,
            "audit_completion_rate": round((audited / len(leads)) * 100, 1) if leads else 0,
            "stage_counts": stage_counts,
            "source_counts": source_counts,
            "owner_counts": owner_counts,
            "open_jobs": sum(1 for job in jobs if job.status in {"pending", "running"}),
        },
        "leads": leads,
        "jobs": jobs,
    }


@router.patch("/{campaign_id}", response_model=CampaignRead)
def update_campaign(
    campaign_id: str,
    payload: CampaignUpdate,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("manage")),
) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(campaign, key, value.value if hasattr(value, "value") else value)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/status", response_model=CampaignRead)
def update_campaign_status(
    campaign_id: str,
    payload: CampaignStatusUpdate,
    db: Session = Depends(get_db),
    _actor=Depends(require_role("manage")),
) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    campaign.status = payload.status.value
    db.commit()
    db.refresh(campaign)
    return campaign

