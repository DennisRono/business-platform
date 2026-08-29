from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import OwnershipController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessOwnerOrAdminUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.ownership import (
    OwnershipRecordCreate,
    OwnershipRecordResponse,
    OwnershipTransitionRequest,
)
from business_platform.utils.constants import AUTH_RESPONSES, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

businesses_owners_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_owners_router.get(
    "/{business_id}/owners",
    summary="List ownership records",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[OwnershipRecordResponse],
)
async def list_owners(
    db: DbSession,
    _: BusinessOwnerOrAdminUser,
    business_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[OwnershipRecordResponse]:
    return await OwnershipController(db).get_all(
        business_id,
        page=page,
        size=size,
        url_base=f"/businesses/{business_id}/owners",
    )


@businesses_owners_router.post(
    "/{business_id}/owners",
    status_code=status.HTTP_201_CREATED,
    summary="Create an ownership record",
    responses=AUTH_RESPONSES,
    response_model=OwnershipRecordResponse,
)
async def create_owner(
    payload: OwnershipRecordCreate,
    db: DbSession,
    _: BusinessOwnerOrAdminUser,
    business_id: uuid.UUID,
) -> OwnershipRecordResponse:
    return await OwnershipController(db).create(business_id, payload.model_dump(exclude_none=True))


@businesses_owners_router.patch(
    "/{business_id}/owners/{ownership_record_id}",
    summary="Transition an ownership record",
    responses=AUTH_RESPONSES,
    response_model=OwnershipRecordResponse,
)
async def transition_owner(
    payload: OwnershipTransitionRequest,
    db: DbSession,
    _: BusinessOwnerOrAdminUser,
    business_id: uuid.UUID,
    ownership_record_id: uuid.UUID,
) -> OwnershipRecordResponse:
    return await OwnershipController(db).transition(
        business_id, ownership_record_id, payload.model_dump(exclude_none=True)
    )
