from __future__ import annotations

import hmac
import time
from hashlib import sha256

from fastapi import HTTPException, Request, status

from app.core.config import get_settings


def signature_payload(
    method: str,
    path: str,
    timestamp: str,
    user_id: str | None,
    role: str | None,
) -> str:
    return "\n".join([method.upper(), path, timestamp, user_id or "", role or ""])


def expected_signature(payload: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()


def verify_signed_request(request: Request) -> None:
    settings = get_settings()
    if not settings.auth_signature_secret:
        return

    timestamp = request.headers.get("X-Siru-Timestamp")
    provided = request.headers.get("X-Siru-Signature")
    if not timestamp or not provided:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Siru request signature.",
        )

    try:
        request_time = int(timestamp)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Siru signature timestamp.",
        ) from exc

    if abs(int(time.time()) - request_time) > settings.auth_signature_tolerance_seconds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired Siru request signature.",
        )

    payload = signature_payload(
        request.method,
        request.url.path,
        timestamp,
        request.headers.get("X-Siru-User-Id"),
        request.headers.get("X-Siru-Role"),
    )
    expected = expected_signature(payload, settings.auth_signature_secret)
    if not hmac.compare_digest(expected, provided):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Siru request signature.",
        )
