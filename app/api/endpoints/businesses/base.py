from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.businesses.index import BusinessController
from business_platform.schemas.business import BusinessCreate, BusinessUpdate
from business_platform.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser
from business_platform.dependencies.authorization import (
    BusinessAccessUser,
    BusinessOwnerOrAdminUser,
)

base_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


# ── Business root ───────────────────────────────────────────────────────────
@base_router.get("/", summary="List businesses")
async def list_businesses(
    db: DbSession,
    current_user: BusinessAccessUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    q: str | None = Query(None),
    sort: str | None = Query(None),
) -> Any:
    return await BusinessController(db).get_all(
        current_user=current_user,
        skip=skip,
        limit=limit,
        q=q,
        sort=sort,
    )


@base_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a business",
)
async def create_business(
    payload: BusinessCreate,
    db: DbSession,
    current_user: GetCurrentUser,
) -> Any:
    return await BusinessController(db).create(
        payload.model_dump(exclude_none=True),
        current_user=current_user,
    )


@base_router.get("/{business_id}", summary="Get a business by id")
async def get_business(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await BusinessController(db).get_by_id(business_id)


@base_router.patch("/{business_id}", summary="Update a business")
async def update_business(
    payload: BusinessUpdate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await BusinessController(db).update(business_id, payload.model_dump(exclude_none=True))


@base_router.delete(
    "/{business_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a business",
)
async def delete_business(
    db: DbSession,
    _: BusinessOwnerOrAdminUser,
    business_id: uuid.UUID,
) -> None:
    await BusinessController(db).delete(business_id)