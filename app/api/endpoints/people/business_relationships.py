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
from business_platform.utils.constants import AUTH_RESPONSES
from business_platform.utils.pagination import PaginationQuery

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
    pagination: PaginationQuery,
) -> PaginatedResponse[PersonBusinessRelationshipResponse]:
    return await PersonController(db).get_business_relationships(
        person_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/people/{person_id}/business-relationships",
    )
