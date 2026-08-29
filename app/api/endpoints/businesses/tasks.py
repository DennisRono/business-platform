from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import EventController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.event import EventResponse
from business_platform.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

businesses_tasks_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_tasks_router.get(
    "/{business_id}/tasks",
    summary="List tasks",
    response_model=PaginatedResponse[EventResponse],
)
async def list_tasks(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    status_filter: str | None = Query(default=None, alias="status", description="Filter by status"),
    start_date: datetime | None = Query(default=None, description="Filter by start date"),
    end_date: datetime | None = Query(default=None, description="Filter by end date"),
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[EventResponse]:
    return await EventController(db).get_all(
        business_id,
        page=page,
        size=size,
        event_type="task",
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
        url_base=f"/businesses/{business_id}/tasks",
    )
