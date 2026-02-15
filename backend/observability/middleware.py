"""
Request/response middleware: request IDs, metrics, and access logging.
"""
import time
import uuid
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from observability.logging_config import request_id_var
from observability.metrics import metrics

logger = logging.getLogger("observability.middleware")

EXCLUDED_PATHS = {"/metrics", "/health"}

PATH_PATTERNS = [
    ("/documents/", "/documents/{filename}"),
]


def normalize_path(path: str) -> str:
    for prefix, replacement in PATH_PATTERNS:
        if path.startswith(prefix) and path != prefix.rstrip("/"):
            return replacement
    return path


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request_id_var.set(req_id)

        path = request.url.path
        method = request.method

        if path in EXCLUDED_PATHS:
            response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            return response

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        status = response.status_code
        norm_path = normalize_path(path)

        metrics.http_requests_total.labels(
            method=method, path=norm_path, status=status
        ).inc()
        metrics.http_request_duration_seconds.labels(
            method=method, path=norm_path
        ).observe(duration)

        logger.info(
            "request completed",
            extra={
                "http_method": method,
                "http_path": path,
                "http_status": status,
                "duration_ms": round(duration * 1000, 2),
            },
        )

        response.headers["X-Request-ID"] = req_id
        return response
