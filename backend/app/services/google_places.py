from __future__ import annotations

import requests

from app.core.config import get_settings


def discover_google_places(country: str, city: str, industry: str, limit: int = 50) -> list[dict]:
    settings = get_settings()
    if not settings.google_places_api_key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY is not configured.")

    query = f"{industry} in {city}, {country}"
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params={"query": query, "key": settings.google_places_api_key},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    results = payload.get("results", [])[:limit]
    leads: list[dict] = []
    for item in results:
        details = place_details(item.get("place_id"))
        leads.append(
            {
                "business_name": item.get("name") or "Unknown Business",
                "website_url": details.get("website"),
                "phone": details.get("formatted_phone_number") or details.get("international_phone_number"),
                "email": None,
                "city": city,
                "country": country,
                "industry": industry,
                "google_rating": item.get("rating"),
                "review_count": item.get("user_ratings_total"),
                "address": item.get("formatted_address"),
                "source_url": details.get("url"),
                "source": "google_places",
                "social_links": {},
            }
        )
    return leads


def place_details(place_id: str | None) -> dict:
    settings = get_settings()
    if not place_id:
        return {}
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        params={
            "place_id": place_id,
            "fields": "website,formatted_phone_number,international_phone_number,url",
            "key": settings.google_places_api_key,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("result", {})

