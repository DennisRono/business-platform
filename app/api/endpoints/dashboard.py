from __future__ import annotations

from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import DashboardController
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser
from business_platform.schemas.aggregates import (
    DashboardOverviewResponse,
    UpcomingItemResponse,
)
from business_platform.schemas.base import PaginatedResponse
from business_platform.utils.constants import AUTH_RESPONSES, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

dashboard_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@dashboard_router.get(
    "/overview",
    summary="Dashboard overview",
    responses=AUTH_RESPONSES,
    response_model=DashboardOverviewResponse,
)
async def overview(db: DbSession, _: GetCurrentUser) -> DashboardOverviewResponse:
    return await DashboardController(db).overview()


@dashboard_router.get(
    "/upcoming",
    summary="Upcoming items",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[UpcomingItemResponse],
)
async def upcoming(
    db: DbSession,
    _: GetCurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[UpcomingItemResponse]:
    return await DashboardController(db).upcoming(
        page=page, size=size, url_base="/dashboard/upcoming"
    )
