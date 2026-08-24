from __future__ import annotations

from fastapi import APIRouter

from .business_relationships import router as business_relationships_router
from .person import router as person_router

router = APIRouter(prefix="/people", tags=["people"])
router.include_router(person_router)
router.include_router(business_relationships_router)