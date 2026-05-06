from __future__ import annotations

import os
from pathlib import Path

import boto3

from app.core.config import get_settings


class ObjectStorage:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.local_root = Path(__file__).resolve().parents[2] / "storage"

    def save_bytes(self, key: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        if self._can_use_s3():
            return self._save_s3(key, content, content_type)
        return self._save_local(key, content)

    def _can_use_s3(self) -> bool:
        return bool(
            self.settings.object_storage_endpoint
            and self.settings.object_storage_access_key
            and self.settings.object_storage_secret_key
        )

    def _save_s3(self, key: str, content: bytes, content_type: str) -> str:
        client = boto3.client(
            "s3",
            endpoint_url=self.settings.object_storage_endpoint,
            aws_access_key_id=self.settings.object_storage_access_key,
            aws_secret_access_key=self.settings.object_storage_secret_key,
        )
        bucket = self.settings.object_storage_bucket
        client.put_object(Bucket=bucket, Key=key, Body=content, ContentType=content_type)
        if self.settings.object_storage_public_base_url:
            return f"{self.settings.object_storage_public_base_url.rstrip('/')}/{key}"
        return f"s3://{bucket}/{key}"

    def _save_local(self, key: str, content: bytes) -> str:
        path = self.local_root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path)


def storage_key(*parts: str) -> str:
    return "/".join(part.strip("/").replace(os.sep, "/") for part in parts if part)

