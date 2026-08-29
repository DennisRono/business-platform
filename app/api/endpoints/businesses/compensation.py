from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import CompensationController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import HrPayrollOrFinanceUser
from business_platform.schemas.aggregates import CompensationSummaryResponse
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.compensation import (
    CompensationRecordCreate,
    CompensationRecordResponse,
)
from business_platform.utils.constants import AUTH_RESPONSES, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

businesses_compensation_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_compensation_router.get(
    "/{business_id}/compensation",
    summary="List compensation records",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[CompensationRecordResponse],
)
async def list_compensation(
    db: DbSession,
    _: HrPayrollOrFinanceUser,
    business_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[CompensationRecordResponse]:
    return await CompensationController(db).get_all(
        business_id,
        page=page,
        size=size,
        url_base=f"/businesses/{business_id}/compensation",
    )


@businesses_compensation_router.post(
    "/{business_id}/compensation",
    status_code=status.HTTP_201_CREATED,
    summary="Create a compensation record",
    responses=AUTH_RESPONSES,
    response_model=CompensationRecordResponse,
)
async def create_compensation(
    payload: CompensationRecordCreate,
    db: DbSession,
    _: HrPayrollOrFinanceUser,
    business_id: uuid.UUID,
) -> CompensationRecordResponse:
    return await CompensationController(db).create(
        business_id, payload.model_dump(exclude_none=True)
    )


@businesses_compensation_router.get(
    "/{business_id}/compensation/{person_id}/history",
    summary="List compensation history for a person",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[CompensationRecordResponse],
)
async def compensation_history(
    db: DbSession,
    _: HrPayrollOrFinanceUser,
    business_id: uuid.UUID,
    person_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[CompensationRecordResponse]:
    return await CompensationController(db).get_history(
        business_id,
        person_id,
        page=page,
        size=size,
        url_base=f"/businesses/{business_id}/compensation/{person_id}/history",
    )


@businesses_compensation_router.get(
    "/{business_id}/compensation/summary",
    summary="Summarize compensation data",
    responses=AUTH_RESPONSES,
    response_model=CompensationSummaryResponse,
)
async def compensation_summary(
    db: DbSession,
    _: HrPayrollOrFinanceUser,
    business_id: uuid.UUID,
) -> CompensationSummaryResponse:
    return await CompensationController(db).summary(business_id)
