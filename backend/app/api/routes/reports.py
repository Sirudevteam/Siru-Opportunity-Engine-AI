from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import DashboardOverview
from app.services.reports import dashboard_overview

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
def overview(db: Session = Depends(get_db)) -> dict:
    return dashboard_overview(db)

