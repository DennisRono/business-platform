from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.businesses.index import BusinessController
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser
from business_platform.dependencies.authorization import (
    BusinessAccessUser,
    BusinessOwnerOrAdminUser,
)
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.business import (
    BusinessCreate,
    BusinessResponse,
    BusinessUpdate,
)
from business_platform.schemas.business_relationship import (
    BusinessRelationshipResponse,
)

from business_platform.utils.constants import (
    AUTH_RESPONSES,
)
from business_platform.utils.pagination import PaginationQuery
from business_platform.utils.pagination import PaginationQuery

base_router = APIRouter()

DbSession: TypeAlias = Annotated[
    AsyncSession,
    Depends(get_db),
]


# ── Business root ────────────────────────────────────────────────────────────


@base_router.get(
    "/",
    summary="List businesses",
    response_model=PaginatedResponse[BusinessResponse],
    responses=AUTH_RESPONSES,
)
async def list_businesses(
    db: DbSession,
    current_user: BusinessAccessUser,
    pagination: PaginationQuery,
    q: str | None = Query(None),
    sort: str | None = Query(None),
) -> PaginatedResponse[BusinessResponse]:
    return await BusinessController(db).get_all(
        current_user=current_user,
        page=pagination.page,
        size=pagination.size,
        q=q,
        sort=sort,
        url_base="/businesses",
    )


@base_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a business",
    response_model=BusinessResponse,
    responses=AUTH_RESPONSES,
)
async def create_business(
    payload: BusinessCreate,
    db: DbSession,
    current_user: GetCurrentUser,
) -> BusinessResponse:
    return await BusinessController(db).create(
        payload.model_dump(exclude_none=True),
        current_user=current_user,
    )


@base_router.get(
    "/{business_id}",
    summary="Get a business by id",
    response_model=BusinessResponse,
    responses=AUTH_RESPONSES,
)
async def get_business(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> BusinessResponse:
    return await BusinessController(db).get_by_id(business_id)


@base_router.patch(
    "/{business_id}",
    summary="Update a business",
    response_model=BusinessResponse,
    responses=AUTH_RESPONSES,
)
async def update_business(
    payload: BusinessUpdate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> BusinessResponse:
    return await BusinessController(db).update(
        business_id,
        payload.model_dump(exclude_none=True),
    )


@base_router.delete(
    "/{business_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a business",
    responses=AUTH_RESPONSES,
)
async def delete_business(
    db: DbSession,
    _: BusinessOwnerOrAdminUser,
    business_id: uuid.UUID,
) -> None:
    await BusinessController(db).delete(business_id)


# ── Business relationships ───────────────────────────────────────────────────


@base_router.get(
    "/{business_id}/relationships",
    summary="List business relationships",
    response_model=PaginatedResponse[BusinessRelationshipResponse],
    responses=AUTH_RESPONSES,
)
async def get_business_relationships(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    pagination: PaginationQuery,
) -> PaginatedResponse[BusinessRelationshipResponse]:
    return await BusinessController(db).get_relationships(
        business_id=business_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/businesses/{business_id}/relationships",
    )


@base_router.post(
    "/{business_id}/relationships",
    status_code=status.HTTP_201_CREATED,
    summary="Create a business relationship",
    response_model=BusinessRelationshipResponse,
    responses=AUTH_RESPONSES,
)
async def create_business_relationship(
    business_id: uuid.UUID,
    payload: dict[str, Any],
    db: DbSession,
    _: BusinessAccessUser,
) -> BusinessRelationshipResponse:
    return await BusinessController(db).create_relationship(
        business_id=business_id,
        payload=payload,
    )
