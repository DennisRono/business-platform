"""In-memory sliding-window rate limiter.

Tracks request timestamps per client key (client IP) in a process-local dict
and rejects requests that exceed ``RATE_LIMIT_REQUESTS`` within
``RATE_LIMIT_WINDOW_SECONDS``. Every response carries ``X-RateLimit-*`` headers.

NOTE: this is per-process and therefore correct only for a single-worker
deployment. In multi-process / multi-pod production, swap this for a shared
store (Redis) or a library such as slowapi so the window is global. That swap
is intentionally isolated to this one module.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from business_platform.core.config import settings
from business_platform.utils.constants import (
    RATE_LIMIT_LIMIT_HEADER,
    RATE_LIMIT_REMAINING_HEADER,
    RATE_LIMIT_RESET_HEADER,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._limit = settings.RATE_LIMIT_REQUESTS
        self._window = settings.RATE_LIMIT_WINDOW_SECONDS
        # client_key -> deque[timestamp] of hits still inside the window
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _client_key(self, request: Request) -> str:
        # Prefer the real client when behind a proxy; fall back to peer address.
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "anonymous"

    async def dispatch(self, request: Request, call_next) -> Response:
        now = time.monotonic()
        key = self._client_key(request)
        window_start = now - self._window

        hits = self._hits[key]
        while hits and hits[0] < window_start:
            hits.popleft()

        reset_after = int(self._window - (now - hits[0])) if hits else self._window

        if len(hits) >= self._limit:
            response: Response = JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "type": "RateLimitError",
                        "message": "Rate limit exceeded. Please slow down.",
                    }
                },
            )
            remaining = 0
        else:
            hits.append(now)
            response = await call_next(request)
            remaining = max(self._limit - len(hits), 0)

        response.headers[RATE_LIMIT_LIMIT_HEADER] = str(self._limit)
        response.headers[RATE_LIMIT_REMAINING_HEADER] = str(remaining)
        response.headers[RATE_LIMIT_RESET_HEADER] = str(reset_after)
        return response
