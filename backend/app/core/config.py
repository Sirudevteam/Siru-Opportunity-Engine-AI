from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = Field(default="local", alias="ENVIRONMENT")
    app_name: str = "Siru Opportunity Engine AI"
    api_prefix: str = "/api/v1"
    frontend_origin: str = Field(default="http://localhost:3000", alias="FRONTEND_ORIGIN")

    database_url: str = Field(default="sqlite:///./siru.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    google_places_api_key: str | None = Field(default=None, alias="GOOGLE_PLACES_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    object_storage_endpoint: str | None = Field(default=None, alias="OBJECT_STORAGE_ENDPOINT")
    object_storage_bucket: str = Field(
        default="siru-opportunity-engine", alias="OBJECT_STORAGE_BUCKET"
    )
    object_storage_access_key: str | None = Field(default=None, alias="OBJECT_STORAGE_ACCESS_KEY")
    object_storage_secret_key: str | None = Field(default=None, alias="OBJECT_STORAGE_SECRET_KEY")
    object_storage_public_base_url: str | None = Field(
        default=None, alias="OBJECT_STORAGE_PUBLIC_BASE_URL"
    )

    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_collection: str = Field(default="website_audits", alias="QDRANT_COLLECTION")

    default_currency: str = Field(default="INR", alias="DEFAULT_CURRENCY")
    crawl_timeout_ms: int = 25_000
    max_crawl_pages: int = 6


@lru_cache
def get_settings() -> Settings:
    return Settings()

