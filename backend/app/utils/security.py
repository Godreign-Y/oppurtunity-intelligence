"""Security helpers for request handling and safe log display."""

import hashlib
import re
import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.responses import JSONResponse

from app.core.config import settings


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization)=([^\s&]+)"),
    re.compile(r"(?i)(bearer\s+)[a-z0-9._\-]+"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
]


def mask_sensitive_text(value: str) -> str:
    masked = value
    masked = SECRET_PATTERNS[0].sub(r"\1=***", masked)
    masked = SECRET_PATTERNS[1].sub(r"\1***", masked)
    masked = SECRET_PATTERNS[2].sub("***.***.***.***", masked)
    masked = SECRET_PATTERNS[3].sub("***@***", masked)
    return masked


def anonymized_client_key(request: Request) -> str:
    host = request.client.host if request.client else "unknown"
    payload = f"{settings.rate_limit_salt}:{host}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allowed(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        if limit <= 0:
            return True
        now = time.monotonic()
        bucket = self._requests[key]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True


rate_limiter = InMemoryRateLimiter()


async def security_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if not rate_limiter.allowed(anonymized_client_key(request), settings.rate_limit_per_minute):
        return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)

    forwarded_proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    https_required = settings.enforce_https or settings.app_env.lower() == "production"
    if https_required and forwarded_proto != "https":
        return JSONResponse({"detail": "HTTPS is required"}, status_code=403)

    response = await call_next(request)
    if settings.security_headers_enabled:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        if https_required:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
