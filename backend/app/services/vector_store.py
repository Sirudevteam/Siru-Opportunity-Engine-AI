from __future__ import annotations

import hashlib

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import EmbeddingRecord, Lead, WebsiteAudit


def try_index_audit(db: Session, lead: Lead, audit: WebsiteAudit) -> None:
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, PointStruct, VectorParams

        settings = get_settings()
        vector = embed_text(
            " ".join(
                [
                    lead.business_name,
                    lead.industry or "",
                    lead.city or "",
                    lead.country or "",
                    audit.problem_summary,
                ]
            )
        )
        client = QdrantClient(url=settings.qdrant_url)
        collections = [collection.name for collection in client.get_collections().collections]
        if settings.qdrant_collection not in collections:
            client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE),
            )
        client.upsert(
            collection_name=settings.qdrant_collection,
            points=[
                PointStruct(
                    id=audit.id,
                    vector=vector,
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
        db.add(
            EmbeddingRecord(
                provider="openai" if settings.openai_api_key else "hash",
                model=settings.openai_embedding_model if settings.openai_api_key else "sha256-local",
                dimensions=len(vector),
                source_object_type="website_audit",
                source_object_id=audit.id,
                vector_id=audit.id,
                metadata_json={"lead_id": lead.id, "campaign_id": lead.campaign_id},
            )
        )
        db.commit()
    except Exception:
        return


def embed_text(text: str) -> list[float]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for embedding indexing.")
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(model=settings.openai_embedding_model, input=text)
    return response.data[0].embedding


def text_to_vector(text: str, size: int = 64) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = []
    for index in range(size):
        byte = digest[index % len(digest)]
        values.append((byte / 255.0) * 2 - 1)
    return values

