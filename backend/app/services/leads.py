from __future__ import annotations

import csv
from io import StringIO
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Campaign, Lead
from app.services.normalization import (
    build_dedupe_key,
    business_value_score,
    contactability_score,
    extract_domain,
    normalize_email,
    normalize_phone,
    normalize_url,
)


FIELD_ALIASES = {
    "business_name": ["business_name", "business name", "name", "company", "company_name"],
    "website_url": ["website_url", "website", "url", "site"],
    "phone": ["phone", "mobile", "telephone", "contact_number"],
    "email": ["email", "mail"],
    "city": ["city", "location_city"],
    "country": ["country"],
    "industry": ["industry", "category", "business_category"],
    "google_rating": ["google_rating", "rating"],
    "review_count": ["review_count", "reviews", "user_ratings_total"],
    "address": ["address", "formatted_address"],
    "source_url": ["source_url", "listing_url", "google_url"],
}


def import_csv_leads(db: Session, campaign: Campaign, content: bytes) -> dict:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    imported = 0
    duplicates = 0
    skipped = 0
    lead_ids: list[str] = []
    for row in reader:
        payload = normalize_csv_row(row, campaign)
        if not payload.get("business_name"):
            skipped += 1
            continue
        lead, created = upsert_lead(db, campaign, payload)
        if created:
            imported += 1
            lead_ids.append(lead.id)
        else:
            duplicates += 1
    db.commit()
    return {
        "campaign_id": campaign.id,
        "imported": imported,
        "duplicates": duplicates,
        "skipped": skipped,
        "lead_ids": lead_ids,
    }


def normalize_csv_row(row: dict[str, Any], campaign: Campaign) -> dict:
    normalized_keys = {key.strip().lower().replace("-", "_"): value for key, value in row.items()}

    def pick(field: str) -> Any:
        for alias in FIELD_ALIASES[field]:
            key = alias.strip().lower().replace("-", "_")
            if key in normalized_keys and normalized_keys[key] not in (None, ""):
                return normalized_keys[key]
        return None

    return {
        "business_name": pick("business_name"),
        "website_url": pick("website_url"),
        "phone": pick("phone"),
        "email": pick("email"),
        "city": pick("city") or campaign.city,
        "country": pick("country") or campaign.country,
        "industry": pick("industry") or campaign.industry,
        "google_rating": parse_float(pick("google_rating")),
        "review_count": parse_int(pick("review_count")),
        "address": pick("address"),
        "source_url": pick("source_url"),
        "source": "csv",
        "social_links": {},
    }


def upsert_lead(db: Session, campaign: Campaign, payload: dict[str, Any]) -> tuple[Lead, bool]:
    website_url = normalize_url(payload.get("website_url"))
    email = normalize_email(payload.get("email"))
    phone = normalize_phone(payload.get("phone"))
    dedupe_key = build_dedupe_key(
        business_name=payload["business_name"],
        website_url=website_url,
        email=email,
        phone=phone,
        city=payload.get("city") or campaign.city,
        country=payload.get("country") or campaign.country,
    )
    existing = db.scalar(
        select(Lead).where(Lead.campaign_id == campaign.id, Lead.dedupe_key == dedupe_key)
    )
    if existing:
        return existing, False

    lead = Lead(
        campaign_id=campaign.id,
        business_name=payload["business_name"].strip(),
        website_url=website_url,
        normalized_domain=extract_domain(website_url),
        phone=phone,
        email=email,
        city=payload.get("city") or campaign.city,
        country=payload.get("country") or campaign.country,
        industry=payload.get("industry") or campaign.industry,
        google_rating=payload.get("google_rating"),
        review_count=payload.get("review_count"),
        address=payload.get("address"),
        source_url=payload.get("source_url"),
        source=payload.get("source") or "manual",
        social_links=payload.get("social_links") or {},
        dedupe_key=dedupe_key,
        contactability_score=contactability_score(email, phone, website_url),
        business_value_score=business_value_score(
            payload.get("google_rating"), payload.get("review_count")
        ),
    )
    db.add(lead)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(Lead).where(Lead.campaign_id == campaign.id, Lead.dedupe_key == dedupe_key)
        )
        if existing:
            return existing, False
        raise
    return lead, True


def parse_float(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def parse_int(value: Any) -> int | None:
    try:
        return int(float(value)) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None

