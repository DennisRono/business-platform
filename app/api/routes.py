from __future__ import annotations

from fastapi import APIRouter

from app.api.endpoints.audit_logs import audit_logs_router
from app.api.endpoints.dashboard import dashboard_router
from app.api.endpoints.contacts import contacts_router
from app.api.endpoints.businesses import businesses_router
from app.api.endpoints.people import people_router
from app.api.endpoints.auth import auth_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/dashboard", tags=["Auth"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(businesses_router, prefix="/business")
api_router.include_router(people_router, prefix="/people", tags=["People"])
api_router.include_router(contacts_router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(audit_logs_router, prefix="/audit-logs", tags=["Audit-Logs"])
