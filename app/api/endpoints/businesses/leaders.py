from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import LeadershipController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.leader import LeaderCreate, LeaderResponse
from business_platform.utils.constants import AUTH_RESPONSES
from business_platform.utils.pagination import PaginationQuery

businesses_leaders_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_leaders_router.get(
    "/{business_id}/leaders",
    summary="List leaders",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[LeaderResponse],
)
async def list_leaders(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    pagination: PaginationQuery,
) -> PaginatedResponse[LeaderResponse]:
    return await LeadershipController(db).get_all(
        business_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/businesses/{business_id}/leaders",
    )


@businesses_leaders_router.post(
    "/{business_id}/leaders",
    status_code=status.HTTP_201_CREATED,
    summary="Create a leader",
    responses=AUTH_RESPONSES,
    response_model=LeaderResponse,
)
async def create_leader(
    payload: LeaderCreate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> LeaderResponse:
    return await LeadershipController(db).create(business_id, payload.model_dump(exclude_none=True))
