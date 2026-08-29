from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import BusinessPeopleController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.person import PersonCreate, PersonResponse
from business_platform.utils.constants import AUTH_RESPONSES
from business_platform.utils.pagination import PaginationQuery

businesses_people_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_people_router.get(
    "/{business_id}/people",
    summary="List people in a business",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[PersonResponse],
)
async def list_people(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    pagination: PaginationQuery,
) -> PaginatedResponse[PersonResponse]:
    return await BusinessPeopleController(db).get_all(
        business_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/businesses/{business_id}/people",
    )


@businesses_people_router.post(
    "/{business_id}/people",
    status_code=status.HTTP_201_CREATED,
    summary="Create a person within a business scope",
    responses=AUTH_RESPONSES,
    response_model=PersonResponse,
)
async def create_person(
    payload: PersonCreate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> PersonResponse:
    return await BusinessPeopleController(db).create(
        business_id, payload.model_dump(exclude_none=True)
    )
