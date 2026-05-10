from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.security import verify_signed_request

logger = logging.getLogger("siru.requests")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        request.state.request_id = request_id
        start = time.perf_counter()
        try:
            if request.url.path.startswith("/api/v1/"):
                verify_signed_request(request)
            response = await call_next(request)
        except HTTPException as exc:
            response = JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-Id"] = request_id
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "elapsed_ms": elapsed_ms,
            },
        )
        return response
