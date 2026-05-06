from __future__ import annotations

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Campaign
from app.schemas import CampaignCreate, CampaignRead, CampaignStatusUpdate, CampaignUpdate

from fastapi import APIRouter

router = APIRouter()


@router.get("", response_model=list[CampaignRead])
def list_campaigns(
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = None,
    db: Session = Depends(get_db),
) -> list[Campaign]:
    query = select(Campaign).order_by(Campaign.created_at.desc())
    if status_filter:
        query = query.where(Campaign.status == status_filter)
    if search:
        like = f"%{search}%"
        query = query.where(Campaign.name.ilike(like))
    return list(db.scalars(query).all())


@router.post("", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)) -> Campaign:
    campaign = Campaign(**payload.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignRead)
def update_campaign(
    campaign_id: str, payload: CampaignUpdate, db: Session = Depends(get_db)
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
    campaign_id: str, payload: CampaignStatusUpdate, db: Session = Depends(get_db)
) -> Campaign:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    campaign.status = payload.status.value
    db.commit()
    db.refresh(campaign)
    return campaign

