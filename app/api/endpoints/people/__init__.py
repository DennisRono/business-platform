from __future__ import annotations

from fastapi import APIRouter

from .business_relationships import people_business_relationships_router
from .person import router as person_router

people_router = APIRouter()

people_router.include_router(person_router)
people_router.include_router(people_business_relationships_router)