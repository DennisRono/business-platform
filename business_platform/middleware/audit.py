"""Audit logging middleware — STUB.

Intent: for every mutating request (POST/PATCH/PUT/DELETE), record an audit
entry capturing the actor, the target resource, the method, and the outcome —
persisted to an ``audit_log`` table so state changes are traceable.

Left as a pass-through stub because meaningful audit records require a real
domain and an actor resolved from auth to reference. Wired into the app now so
turning it on later needs no structural change.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_MUTATING_METHODS = {"POST", "PATCH", "PUT", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        if request.method in _MUTATING_METHODS:
            # Will persist an audit entry (actor, resource, method, status)
            # for this mutating request.
            pass
        return response
