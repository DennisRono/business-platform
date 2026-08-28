from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import EventController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser

businesses_tasks_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_tasks_router.get("/{business_id}/tasks", summary="List tasks")
async def list_tasks(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    status_filter: str | None = Query(default=None, alias="status", description="Filter by status"),
    start_date: datetime | None = Query(default=None, description="Filter by start date"),
    end_date: datetime | None = Query(default=None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    return await EventController(db).get_all(
        business_id,
        event_type="task",
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )