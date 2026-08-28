from __future__ import annotations

from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import DashboardController
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser

dashboard_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@dashboard_router .get("/overview", summary="Dashboard overview")
async def overview(db: DbSession, _: GetCurrentUser) -> Any:
    return await DashboardController(db).overview()


@dashboard_router .get("/upcoming", summary="Upcoming items")
async def upcoming(db: DbSession, _: GetCurrentUser) -> Any:
    return await DashboardController(db).upcoming()