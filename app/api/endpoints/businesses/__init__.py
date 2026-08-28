from __future__ import annotations

from fastapi import APIRouter

from app.api.endpoints.businesses.base import base_router
from app.api.endpoints.businesses.compensation import businesses_compensation_router
from app.api.endpoints.businesses.documents import businesses_documents_router
from app.api.endpoints.businesses.employees import businesses_employees_router
from app.api.endpoints.businesses.events import businesses_events_router
from app.api.endpoints.businesses.financials import businesses_financials_router
from app.api.endpoints.businesses.leaders import businesses_leaders_router
from app.api.endpoints.businesses.memberships import businesses_memberships_router
from app.api.endpoints.businesses.owners import businesses_owners_router
from app.api.endpoints.businesses.people import businesses_people_router
from app.api.endpoints.businesses.relationships import businesses_relationships_router
from app.api.endpoints.businesses.taxes import businesses_taxes_router
from app.api.endpoints.businesses.tasks import businesses_tasks_router

businesses_router = APIRouter()

businesses_router.include_router(base_router, tags=["Business"])
businesses_router.include_router(businesses_relationships_router, tags=["Business Relationships"])
businesses_router.include_router(businesses_memberships_router, tags=["Business Memberships"])
businesses_router.include_router(businesses_people_router, tags=["Business People"])
businesses_router.include_router(businesses_owners_router, tags=["Business Owners"])
businesses_router.include_router(businesses_leaders_router, tags=["Business Leaders"])
businesses_router.include_router(businesses_employees_router, tags=["Business Employees"])
businesses_router.include_router(businesses_compensation_router, tags=["Business Compensation"])
businesses_router.include_router(businesses_taxes_router, tags=["Business Taxes"])
businesses_router.include_router(businesses_documents_router, tags=["Business Documents"])
businesses_router.include_router(businesses_events_router, tags=["Business Events"])
businesses_router.include_router(businesses_tasks_router, tags=["Business Tasks"])
businesses_router.include_router(businesses_financials_router, tags=["Business Financials"])
