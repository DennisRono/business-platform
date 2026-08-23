"""Permission checker middleware — STUB.

Intent: before a handler runs, resolve the set of permissions the matched route
requires and verify the authenticated caller's role grants them, raising
:class:`AuthorizationError` otherwise. Route-to-permission mapping would come
from a registry keyed by route name, and role-to-permission grants from the
seeded permission tables.

Left as a pass-through stub because permission resolution depends on at least
one real domain (and seeded permission data) existing to operate on — see the
"Recommended Build Order" in the design document. It is wired into the app so
enabling it later is a one-line change, not a re-plumb.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class PermissionCheckerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Will resolve required permissions for the matched route and check them
        # against the caller's role before delegating to the handler.
        return await call_next(request)
