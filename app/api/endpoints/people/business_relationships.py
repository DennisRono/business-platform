from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import PersonController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import CrossBusinessPersonUser
from business_platform.schemas.aggregates import PersonBusinessRelationshipResponse
from business_platform.schemas.base import PaginatedResponse
from business_platform.utils.constants import AUTH_RESPONSES, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

people_business_relationships_router = APIRouter(tags=["people"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@people_business_relationships_router.get(
    "/{person_id}/business-relationships",
    summary="List person business relationships",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[PersonBusinessRelationshipResponse],
)
async def list_business_relationships(
    db: DbSession,
    _: CrossBusinessPersonUser,
    person_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[PersonBusinessRelationshipResponse]:
    return await PersonController(db).get_business_relationships(
        person_id,
        page=page,
        size=size,
        url_base=f"/people/{person_id}/business-relationships",
    )
