from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import EmployeeController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.employee import (
    EmployeeCreate,
    EmployeeHistoryResponse,
    EmployeeResponse,
    EmployeeTerminateRequest,
)
from business_platform.utils.constants import AUTH_RESPONSES
from business_platform.utils.pagination import PaginationQuery

businesses_employees_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_employees_router.get(
    "/{business_id}/employees",
    summary="List employees",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[EmployeeResponse],
)
async def list_employees(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    pagination: PaginationQuery,
) -> PaginatedResponse[EmployeeResponse]:
    return await EmployeeController(db).get_all(
        business_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/businesses/{business_id}/employees",
    )


@businesses_employees_router.post(
    "/{business_id}/employees",
    status_code=status.HTTP_201_CREATED,
    summary="Create an employee record",
    responses=AUTH_RESPONSES,
    response_model=EmployeeResponse,
)
async def create_employee(
    payload: EmployeeCreate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> EmployeeResponse:
    return await EmployeeController(db).create(business_id, payload.model_dump(exclude_none=True))


@businesses_employees_router.get(
    "/{business_id}/employees/{person_id}/history",
    summary="List employee history",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[EmployeeHistoryResponse],
)
async def employee_history(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    person_id: uuid.UUID,
    pagination: PaginationQuery,
) -> PaginatedResponse[EmployeeHistoryResponse]:
    return await EmployeeController(db).get_history(
        business_id,
        person_id,
        page=pagination.page,
        size=pagination.size,
        url_base=f"/businesses/{business_id}/employees/{person_id}/history",
    )


@businesses_employees_router.post(
    "/{business_id}/employees/{person_id}/terminate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Terminate an employee",
)
async def terminate_employee(
    payload: EmployeeTerminateRequest,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    person_id: uuid.UUID,
) -> None:
    await EmployeeController(db).terminate(
        business_id, person_id, payload.model_dump(exclude_none=True)
    )
