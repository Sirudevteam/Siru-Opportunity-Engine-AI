from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Campaign, CampaignStatus, CRMStage, Lead, Proposal, WebsiteAudit


def dashboard_overview(db: Session) -> dict:
    total_campaigns = db.scalar(select(func.count(Campaign.id))) or 0
    running_campaigns = (
        db.scalar(select(func.count(Campaign.id)).where(Campaign.status == CampaignStatus.running.value))
        or 0
    )
    total_leads = db.scalar(select(func.count(Lead.id))) or 0
    audited_leads = db.scalar(select(func.count(WebsiteAudit.id))) or 0
    proposals = db.scalar(select(func.count(Proposal.id))) or 0
    won = db.scalar(select(func.count(Lead.id)).where(Lead.crm_stage == CRMStage.won.value)) or 0
    lost = db.scalar(select(func.count(Lead.id)).where(Lead.crm_stage == CRMStage.lost.value)) or 0
    average_score = db.scalar(select(func.avg(Lead.final_lead_score)).where(Lead.final_lead_score.is_not(None)))

    stage_counts = {}
    for stage in CRMStage:
        stage_counts[stage.value] = (
            db.scalar(select(func.count(Lead.id)).where(Lead.crm_stage == stage.value)) or 0
        )

    priority_counts = {}
    for priority in ["very_hot", "hot", "warm", "low_priority"]:
        priority_counts[priority] = (
            db.scalar(select(func.count(Lead.id)).where(Lead.priority_category == priority)) or 0
        )

    return {
        "campaigns": {"total": total_campaigns, "running": running_campaigns},
        "leads": {
            "total": total_leads,
            "audited": audited_leads,
            "average_final_score": round(float(average_score), 1) if average_score else 0,
            "priority_counts": priority_counts,
        },
        "audits": {"completed": audited_leads},
        "crm": {"stage_counts": stage_counts, "won": won, "lost": lost},
        "proposals": {"total": proposals},
        "sales": {
            "conversion_rate": round((won / total_leads) * 100, 1) if total_leads else 0,
            "open_pipeline": total_leads - won - lost,
        },
    }

