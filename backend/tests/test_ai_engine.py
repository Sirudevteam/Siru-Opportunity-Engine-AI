from app.models import Lead, WebsiteAudit
from app.services.ai_engine import fallback_ai_audit


def test_fallback_ai_audit_for_weak_site():
    lead = Lead(
        campaign_id="campaign",
        business_name="Example Dental",
        dedupe_key="domain:example.com",
        website_url="https://example.com",
    )
    audit = WebsiteAudit(
        lead_id="lead",
        total_score=38,
        lead_priority="very_hot",
        problem_summary="Website score is 38/100.",
    )
    output = fallback_ai_audit(lead, audit, "INR")
    assert output["closing_probability"] == 74
    assert "Website Redesign" in output["recommended_service"]

