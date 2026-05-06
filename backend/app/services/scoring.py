from __future__ import annotations

from app.models import LeadPriority


SCORE_WEIGHTS = {
    "ui_ux_design_quality": 20,
    "mobile_responsiveness": 15,
    "page_speed": 15,
    "seo_basics": 15,
    "conversion_cta": 15,
    "trust_signals": 10,
    "technology_modernity": 10,
}


def clamp(value: int | float, minimum: int = 0, maximum: int = 100) -> int:
    return int(max(minimum, min(maximum, round(value))))


def priority_for_website_score(score: int) -> LeadPriority:
    if score <= 40:
        return LeadPriority.very_hot
    if score <= 60:
        return LeadPriority.hot
    if score <= 75:
        return LeadPriority.warm
    return LeadPriority.low_priority


def final_lead_score(
    website_score: int | None,
    business_value: int,
    contactability: int,
    industry_priority: int,
    location_priority: int,
    ai_closing_probability: int | None,
) -> int:
    weakness_score = 100 - website_score if website_score is not None else 50
    closing_probability = ai_closing_probability if ai_closing_probability is not None else 55
    return clamp(
        (
            weakness_score
            + business_value
            + contactability
            + industry_priority
            + location_priority
            + closing_probability
        )
        / 6
    )


def score_website_checks(checks: dict) -> dict:
    seo = 0
    seo += 4 if checks.get("has_title") else 0
    seo += 4 if checks.get("has_meta_description") else 0
    seo += 3 if checks.get("has_h1") else 0
    seo += 2 if checks.get("image_alt_ratio", 0) >= 0.65 else 0
    seo += 2 if checks.get("canonical_url") else 0

    ctas = checks.get("cta_count", 0)
    conversion = 0
    conversion += 5 if ctas >= 1 else 0
    conversion += 4 if ctas >= 3 else 0
    conversion += 3 if checks.get("form_count", 0) >= 1 else 0
    conversion += 3 if checks.get("has_phone_or_email") else 0

    trust = 0
    trust += 3 if checks.get("has_https") else 0
    trust += 2 if checks.get("has_address") else 0
    trust += 2 if checks.get("social_link_count", 0) >= 1 else 0
    trust += 2 if checks.get("has_schema_org") else 0
    trust += 1 if checks.get("has_testimonial_terms") else 0

    mobile = 0
    mobile += 8 if checks.get("has_viewport_meta") else 0
    mobile += 4 if checks.get("has_responsive_css") else 0
    mobile += 3 if checks.get("mobile_screenshot") else 0

    page_size_kb = checks.get("page_size_kb", 0)
    response_ms = checks.get("response_ms", 0)
    speed = 15
    if page_size_kb > 1500:
        speed -= 5
    elif page_size_kb > 800:
        speed -= 3
    if response_ms > 3500:
        speed -= 5
    elif response_ms > 1800:
        speed -= 3
    speed = clamp(speed, 0, 15)

    ui = 0
    ui += 4 if checks.get("has_navigation") else 0
    ui += 4 if checks.get("has_service_or_product_links") else 0
    ui += 3 if checks.get("text_length", 0) >= 700 else 0
    ui += 3 if checks.get("image_count", 0) >= 3 else 0
    ui += 3 if checks.get("has_contact_page") else 0
    ui += 3 if checks.get("has_about_page") else 0

    tech = 0
    tech += 4 if checks.get("has_https") else 0
    tech += 3 if checks.get("uses_modern_framework") else 0
    tech += 2 if checks.get("has_structured_assets") else 0
    tech += 1 if not checks.get("old_tech_signals") else 0

    scores = {
        "ui_ux_design_quality": clamp(ui, 0, SCORE_WEIGHTS["ui_ux_design_quality"]),
        "mobile_responsiveness": clamp(mobile, 0, SCORE_WEIGHTS["mobile_responsiveness"]),
        "page_speed": clamp(speed, 0, SCORE_WEIGHTS["page_speed"]),
        "seo_basics": clamp(seo, 0, SCORE_WEIGHTS["seo_basics"]),
        "conversion_cta": clamp(conversion, 0, SCORE_WEIGHTS["conversion_cta"]),
        "trust_signals": clamp(trust, 0, SCORE_WEIGHTS["trust_signals"]),
        "technology_modernity": clamp(tech, 0, SCORE_WEIGHTS["technology_modernity"]),
    }
    total = sum(scores.values())
    return {
        "total_score": total,
        "lead_priority": priority_for_website_score(total).value,
        "scores": scores,
        "problem_summary": summarize_score(total, scores),
    }


def summarize_score(total: int, scores: dict[str, int]) -> str:
    weak_categories = [
        label.replace("_", " ")
        for label, max_score in SCORE_WEIGHTS.items()
        if scores.get(label, 0) <= max_score * 0.55
    ]
    if total <= 40:
        lead_type = "very strong sales opportunity"
    elif total <= 60:
        lead_type = "strong improvement opportunity"
    elif total <= 75:
        lead_type = "moderate opportunity"
    else:
        lead_type = "lower priority opportunity"
    if weak_categories:
        return f"Website score is {total}/100, a {lead_type}. Weakest areas: {', '.join(weak_categories[:3])}."
    return f"Website score is {total}/100, a {lead_type}. The site has no major obvious weakness from automated checks."

