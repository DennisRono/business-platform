from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import FinancialController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.aggregates import FinancialSummaryResponse
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.financial import (
    FinancialAccountResponse,
    FinancialTransactionCreate,
    FinancialTransactionResponse,
)
from business_platform.utils.constants import AUTH_RESPONSES
from business_platform.utils.pagination import PaginationQuery

businesses_financials_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_financials_router.get(
    "/{business_id}/financials/transactions",
    summary="List financial transactions",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[FinancialTransactionResponse],
)
async def list_transactions(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    pagination: PaginationQuery,
) -> PaginatedResponse[FinancialTransactionResponse]:
    return await FinancialController(db).get_transactions(
        business_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/businesses/{business_id}/financials/transactions",
    )


@businesses_financials_router.post(
    "/{business_id}/financials/transactions",
    status_code=status.HTTP_201_CREATED,
    summary="Create a financial transaction",
    responses=AUTH_RESPONSES,
    response_model=FinancialTransactionResponse,
)
async def create_transaction(
    payload: FinancialTransactionCreate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> FinancialTransactionResponse:
    return await FinancialController(db).create_transaction(
        business_id, payload.model_dump(exclude_none=True)
    )


@businesses_financials_router.get(
    "/{business_id}/financials/accounts",
    summary="List financial accounts",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[FinancialAccountResponse],
)
async def list_accounts(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    pagination: PaginationQuery,
) -> PaginatedResponse[FinancialAccountResponse]:
    return await FinancialController(db).get_accounts(
        business_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/businesses/{business_id}/financials/accounts",
    )


@businesses_financials_router.get(
    "/{business_id}/financials/summary",
    summary="Summarize financials",
    responses=AUTH_RESPONSES,
    response_model=FinancialSummaryResponse,
)
async def financial_summary(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> FinancialSummaryResponse:
    return await FinancialController(db).summary(business_id)
