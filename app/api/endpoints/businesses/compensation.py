from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import CompensationController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import HrPayrollOrFinanceUser

businesses_compensation_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_compensation_router.get("/{business_id}/compensation", summary="List compensation records")
async def list_compensation(
    db: DbSession,
    _: HrPayrollOrFinanceUser,
    business_id: uuid.UUID,
) -> Any:
    return await CompensationController(db).get_all(business_id)


@businesses_compensation_router.post(
    "/{business_id}/compensation",
    status_code=status.HTTP_201_CREATED,
    summary="Create a compensation record",
)
async def create_compensation(
    payload: dict[str, Any],
    db: DbSession,
    _: HrPayrollOrFinanceUser,
    business_id: uuid.UUID,
) -> Any:
    return await CompensationController(db).create(business_id, payload)


@businesses_compensation_router.get(
    "/{business_id}/compensation/{person_id}/history",
    summary="List compensation history for a person",
)
async def compensation_history(
    db: DbSession,
    _: HrPayrollOrFinanceUser,
    business_id: uuid.UUID,
    person_id: uuid.UUID,
) -> Any:
    return await CompensationController(db).get_history(business_id, person_id)


@businesses_compensation_router.get(
    "/{business_id}/compensation/summary",
    summary="Summarize compensation data",
)
async def compensation_summary(
    db: DbSession,
    _: HrPayrollOrFinanceUser,
    business_id: uuid.UUID,
) -> Any:
    return await CompensationController(db).summary(business_id)