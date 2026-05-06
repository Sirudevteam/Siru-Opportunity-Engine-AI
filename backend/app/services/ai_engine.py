from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.models import Lead, WebsiteAudit


class AIAuditOutput(BaseModel):
    problem_summary: str
    business_risk: str
    improvement_opportunities: list[str] = Field(default_factory=list)
    recommended_service: str
    estimated_project_value: str
    outreach_angle: str
    closing_probability: int = Field(ge=0, le=100)


def generate_ai_audit(lead: Lead, audit: WebsiteAudit, currency: str = "INR") -> dict:
    settings = get_settings()
    fallback = fallback_ai_audit(lead, audit, currency)
    if not settings.openai_api_key:
        return fallback | {"raw_response": {"mode": "fallback", "reason": "OPENAI_API_KEY missing"}}

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        response = client.responses.parse(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are Siru's internal website audit strategist. Return concise, sales-useful "
                        "structured JSON for a manual outreach workflow. Do not claim outreach was sent."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Business: {lead.business_name}\n"
                        f"Industry: {lead.industry}\n"
                        f"Location: {lead.city}, {lead.country}\n"
                        f"Website score: {audit.total_score}/100\n"
                        f"Automated summary: {audit.problem_summary}\n"
                        f"Score details: {audit.raw_checks}\n"
                        f"Currency: {currency}"
                    ),
                },
            ],
            text_format=AIAuditOutput,
        )
        parsed = response.output_parsed
        if parsed is None:
            return fallback | {"raw_response": {"mode": "fallback", "reason": "empty AI response"}}
        return parsed.model_dump() | {"raw_response": {"mode": "openai", "model": settings.openai_model}}
    except Exception as exc:
        return fallback | {"raw_response": {"mode": "fallback", "error": str(exc)}}


def fallback_ai_audit(lead: Lead, audit: WebsiteAudit, currency: str) -> dict:
    if audit.total_score <= 40:
        probability = 74
        deal = f"{currency} 75,000 - {currency} 250,000"
        service = "Website Redesign + Local SEO"
    elif audit.total_score <= 60:
        probability = 62
        deal = f"{currency} 50,000 - {currency} 150,000"
        service = "Conversion Website Refresh + SEO"
    else:
        probability = 42
        deal = f"{currency} 30,000 - {currency} 90,000"
        service = "SEO and Conversion Optimization"

    return {
        "problem_summary": audit.problem_summary,
        "business_risk": (
            "The current website may be losing mobile visitors, local search visibility, "
            "and enquiry conversions compared with stronger competitors."
        ),
        "improvement_opportunities": [
            "Improve mobile layout and page structure.",
            "Strengthen SEO basics, headings, metadata, and local intent pages.",
            "Add clearer calls to action, trust signals, and contact paths.",
        ],
        "recommended_service": service,
        "estimated_project_value": deal,
        "outreach_angle": (
            f"Lead with a short free audit for {lead.business_name}, focused on enquiries and "
            "mobile visitors rather than technical criticism."
        ),
        "closing_probability": probability,
    }

