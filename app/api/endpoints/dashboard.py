from __future__ import annotations

from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import DashboardController
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.get("/overview", summary="Dashboard overview")
async def overview(db: DbSession, _: GetCurrentUser) -> Any:
    return await DashboardController(db).overview()


@router.get("/upcoming", summary="Upcoming items")
async def upcoming(db: DbSession, _: GetCurrentUser) -> Any:
    return await DashboardController(db).upcoming()