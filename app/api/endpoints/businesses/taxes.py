from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import TaxController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import (
    BusinessAccessUser,
    SensitiveDataUser,
)
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.tax import (
    TaxIdentifierCreate,
    TaxIdentifierResponse,
    TaxProfileCreate,
    TaxProfileResponse,
)
from business_platform.utils.constants import AUTH_RESPONSES
from business_platform.utils.pagination import PaginationQuery

businesses_taxes_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_taxes_router.get(
    "/{business_id}/taxes",
    summary="List tax profiles",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[TaxProfileResponse],
)
async def list_taxes(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    pagination: PaginationQuery,
) -> PaginatedResponse[TaxProfileResponse]:
    return await TaxController(db).get_all(
        business_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/businesses/{business_id}/taxes",
    )


@businesses_taxes_router.post(
    "/{business_id}/taxes",
    status_code=status.HTTP_201_CREATED,
    summary="Create a tax profile",
    responses=AUTH_RESPONSES,
    response_model=TaxProfileResponse,
)
async def create_tax_profile(
    payload: TaxProfileCreate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> TaxProfileResponse:
    return await TaxController(db).create(business_id, payload.model_dump(exclude_none=True))


@businesses_taxes_router.get(
    "/{business_id}/taxes/{tax_profile_id}/identifiers",
    summary="List sensitive tax identifiers",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[TaxIdentifierResponse],
)
async def list_tax_identifiers(
    db: DbSession,
    _: SensitiveDataUser,
    business_id: uuid.UUID,
    tax_profile_id: uuid.UUID,
    pagination: PaginationQuery,
) -> PaginatedResponse[TaxIdentifierResponse]:
    # TODO: make this request auditable through the audit dependency pipeline.
    return await TaxController(db).get_identifiers(
        business_id,
        tax_profile_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/businesses/{business_id}/taxes/{tax_profile_id}/identifiers",
    )
