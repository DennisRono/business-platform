from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import MembershipController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import (
    BusinessOwnerOrAdminUser,
)
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.membership import (
    MembershipCreate,
    MembershipResponse,
    MembershipUpdate,
)
from business_platform.utils.constants import (
    AUTH_RESPONSES,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)

businesses_memberships_router = APIRouter()

DbSession: TypeAlias = Annotated[
    AsyncSession,
    Depends(get_db),
]


@businesses_memberships_router.get(
    "/{business_id}/memberships",
    summary="List business memberships",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[MembershipResponse],
)
async def list_memberships(
    db: DbSession,
    _: BusinessOwnerOrAdminUser,
    business_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
    ),
) -> PaginatedResponse[MembershipResponse]:
    return await MembershipController(db).get_all(
        business_id=business_id,
        page=page,
        size=size,
        url_base=f"/businesses/{business_id}/memberships",
    )


@businesses_memberships_router.post(
    "/{business_id}/memberships",
    status_code=status.HTTP_201_CREATED,
    summary="Create a membership",
    responses=AUTH_RESPONSES,
    response_model=MembershipResponse,
)
async def create_membership(
    payload: MembershipCreate,
    db: DbSession,
    current_user: BusinessOwnerOrAdminUser,
    business_id: uuid.UUID,
) -> MembershipResponse:
    return await MembershipController(db).create(
        business_id=business_id,
        payload=payload.model_dump(exclude_none=True),
        invited_by_id=current_user.id,
    )


@businesses_memberships_router.patch(
    "/{business_id}/memberships/{membership_id}",
    summary="Update a membership",
    responses=AUTH_RESPONSES,
    response_model=MembershipResponse,
)
async def update_membership(
    payload: MembershipUpdate,
    db: DbSession,
    _: BusinessOwnerOrAdminUser,
    business_id: uuid.UUID,
    membership_id: uuid.UUID,
) -> MembershipResponse:
    return await MembershipController(db).update(
        business_id=business_id,
        membership_id=membership_id,
        payload=payload.model_dump(exclude_none=True),
    )
