from app.models import LeadPriority
from app.services.scoring import final_lead_score, priority_for_website_score, score_website_checks


def test_priority_boundaries():
    assert priority_for_website_score(40) == LeadPriority.very_hot
    assert priority_for_website_score(41) == LeadPriority.hot
    assert priority_for_website_score(61) == LeadPriority.warm
    assert priority_for_website_score(76) == LeadPriority.low_priority


def test_final_lead_score_uses_website_weakness():
    score = final_lead_score(
        website_score=35,
        business_value=80,
        contactability=90,
        industry_priority=80,
        location_priority=75,
        ai_closing_probability=70,
    )
    assert score == 77


def test_score_website_checks_detects_hot_lead():
    result = score_website_checks(
        {
            "has_title": False,
            "has_meta_description": False,
            "has_h1": False,
            "image_alt_ratio": 0,
            "cta_count": 0,
            "form_count": 0,
            "has_phone_or_email": False,
            "has_https": False,
            "has_viewport_meta": False,
            "page_size_kb": 1800,
            "response_ms": 4200,
            "text_length": 100,
            "image_count": 0,
            "old_tech_signals": True,
        }
    )
    assert result["total_score"] <= 40
    assert result["lead_priority"] == "very_hot"

