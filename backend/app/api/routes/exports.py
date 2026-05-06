from __future__ import annotations

import csv
from io import StringIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Campaign, Lead, Proposal, WebsiteAudit

router = APIRouter()


@router.get("/leads.csv")
def export_leads(db: Session = Depends(get_db)) -> StreamingResponse:
    rows = db.scalars(select(Lead).order_by(Lead.created_at.desc())).all()
    return csv_response(
        "leads.csv",
        [
            "id",
            "campaign_id",
            "business_name",
            "website_url",
            "phone",
            "email",
            "city",
            "country",
            "industry",
            "website_score",
            "final_lead_score",
            "priority_category",
            "crm_stage",
        ],
        rows,
    )


@router.get("/audits.csv")
def export_audits(db: Session = Depends(get_db)) -> StreamingResponse:
    rows = db.scalars(select(WebsiteAudit).order_by(WebsiteAudit.created_at.desc())).all()
    return csv_response(
        "audits.csv",
        ["id", "lead_id", "website_id", "total_score", "lead_priority", "problem_summary", "created_at"],
        rows,
    )


@router.get("/crm.csv")
def export_crm(db: Session = Depends(get_db)) -> StreamingResponse:
    rows = db.scalars(select(Lead).order_by(Lead.updated_at.desc())).all()
    return csv_response(
        "crm.csv",
        ["id", "business_name", "crm_stage", "owner_id", "owner_name", "final_lead_score", "updated_at"],
        rows,
    )


@router.get("/campaigns.csv")
def export_campaigns(db: Session = Depends(get_db)) -> StreamingResponse:
    rows = db.scalars(select(Campaign).order_by(Campaign.created_at.desc())).all()
    return csv_response(
        "campaigns.csv",
        ["id", "name", "country", "city", "industry", "target_leads", "status", "created_at"],
        rows,
    )


@router.get("/proposals.csv")
def export_proposals(db: Session = Depends(get_db)) -> StreamingResponse:
    rows = db.scalars(select(Proposal).order_by(Proposal.created_at.desc())).all()
    return csv_response(
        "proposals.csv",
        ["id", "lead_id", "title", "estimated_value", "status", "pdf_url", "created_at"],
        rows,
    )


def csv_response(filename: str, headers: list[str], rows) -> StreamingResponse:
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow({header: getattr(row, header, None) for header in headers})
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

