from __future__ import annotations

from fastapi import APIRouter

from app.api.endpoints import audit_logs, contacts, dashboard
from app.api.endpoints.businesses import router as businesses_router
from app.api.endpoints.people import router as people_router
from app.api.endpoints.auth import auth_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(businesses_router)
api_router.include_router(people_router)
api_router.include_router(contacts.router)
api_router.include_router(dashboard.router)
api_router.include_router(audit_logs.router)
