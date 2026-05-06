from fastapi import APIRouter

from app.api.routes import audits, campaigns, crm, exports, leads, outreach, proposals, reports

api_router = APIRouter()
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(audits.router, prefix="/audits", tags=["audits"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["outreach"])
api_router.include_router(crm.router, prefix="/crm", tags=["crm"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["proposals"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])

