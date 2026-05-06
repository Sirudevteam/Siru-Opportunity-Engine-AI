from __future__ import annotations

import re
from urllib.parse import urlparse, urlunparse


def normalize_url(value: str | None) -> str | None:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    netloc = parsed.netloc.lower().strip()
    path = parsed.path.rstrip("/")
    return urlunparse((parsed.scheme.lower(), netloc, path, "", "", ""))


def extract_domain(value: str | None) -> str | None:
    normalized = normalize_url(value)
    if not normalized:
        return None
    host = urlparse(normalized).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def normalize_email(value: str | None) -> str | None:
    if not value:
        return None
    email = value.strip().lower()
    return email if "@" in email else None


def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"[^\d+]", "", value)
    return cleaned or None


def slug_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def build_dedupe_key(
    business_name: str,
    website_url: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    city: str | None = None,
    country: str | None = None,
) -> str:
    domain = extract_domain(website_url)
    if domain:
        return f"domain:{domain}"
    normalized_email = normalize_email(email)
    if normalized_email:
        return f"email:{normalized_email}"
    normalized_phone = normalize_phone(phone)
    if normalized_phone:
        return f"phone:{normalized_phone}"
    return "name:" + "|".join([slug_text(business_name), slug_text(city), slug_text(country)])


def contactability_score(email: str | None, phone: str | None, website_url: str | None) -> int:
    score = 20
    if website_url:
        score += 25
    if phone:
        score += 25
    if email:
        score += 30
    return min(score, 100)


def business_value_score(google_rating: float | None, review_count: int | None) -> int:
    score = 50
    if google_rating:
        score += int(min(google_rating, 5) * 6)
    if review_count:
        score += min(review_count // 5, 20)
    return max(0, min(score, 100))

