from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import FinancialController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser

businesses_financials_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_financials_router.get("/{business_id}/financials/transactions", summary="List financial transactions")
async def list_transactions(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await FinancialController(db).get_transactions(business_id)


@businesses_financials_router.post(
    "/{business_id}/financials/transactions",
    status_code=status.HTTP_201_CREATED,
    summary="Create a financial transaction",
)
async def create_transaction(
    payload: dict[str, Any],
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await FinancialController(db).create_transaction(business_id, payload)


@businesses_financials_router.get("/{business_id}/financials/accounts", summary="List financial accounts")
async def list_accounts(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await FinancialController(db).get_accounts(business_id)


@businesses_financials_router.get("/{business_id}/financials/summary", summary="Summarize financials")
async def financial_summary(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await FinancialController(db).summary(business_id)