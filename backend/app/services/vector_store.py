from __future__ import annotations

import hashlib

from app.core.config import get_settings
from app.models import Lead, WebsiteAudit


def try_index_audit(lead: Lead, audit: WebsiteAudit) -> None:
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, PointStruct, VectorParams

        settings = get_settings()
        client = QdrantClient(url=settings.qdrant_url)
        collections = [collection.name for collection in client.get_collections().collections]
        if settings.qdrant_collection not in collections:
            client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(size=64, distance=Distance.COSINE),
            )
        text = " ".join(
            [
                lead.business_name,
                lead.industry or "",
                lead.city or "",
                lead.country or "",
                audit.problem_summary,
            ]
        )
        client.upsert(
            collection_name=settings.qdrant_collection,
            points=[
                PointStruct(
                    id=audit.id,
                    vector=text_to_vector(text),
                    payload={
                        "lead_id": lead.id,
                        "campaign_id": lead.campaign_id,
                        "business_name": lead.business_name,
                        "website_score": audit.total_score,
                        "priority": audit.lead_priority,
                    },
                )
            ],
        )
    except Exception:
        return


def text_to_vector(text: str, size: int = 64) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = []
    for index in range(size):
        byte = digest[index % len(digest)]
        values.append((byte / 255.0) * 2 - 1)
    return values

