from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import EventController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.event import EventCreate, EventResponse, EventUpdate
from business_platform.utils.constants import AUTH_RESPONSES
from business_platform.utils.pagination import PaginationQuery

businesses_events_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_events_router.get(
    "/{business_id}/events",
    summary="List events",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[EventResponse],
)
async def list_events(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    pagination: PaginationQuery,
    event_type: str | None = Query(default=None, description="Filter by event type"),
    event_status: str | None = Query(default=None, alias="status", description="Filter by status"),
    start_date: datetime | None = Query(default=None, description="Filter by start date"),
    end_date: datetime | None = Query(default=None, description="Filter by end date"),
) -> PaginatedResponse[EventResponse]:
    return await EventController(db).get_all(
        business_id,
        page=pagination.page,
        size=pagination.size,
        event_type=event_type,
        status=event_status,
        start_date=start_date,
        end_date=end_date,
        url_base=f"/businesses/{business_id}/events",
    )


@businesses_events_router.post(
    "/{business_id}/events",
    status_code=status.HTTP_201_CREATED,
    summary="Create an event",
    responses=AUTH_RESPONSES,
    response_model=EventResponse,
)
async def create_event(
    payload: EventCreate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> EventResponse:
    return await EventController(db).create(business_id, payload.model_dump(exclude_none=True))


@businesses_events_router.patch(
    "/{business_id}/events/{event_id}",
    summary="Update an event",
    responses=AUTH_RESPONSES,
    response_model=EventResponse,
)
async def update_event(
    payload: EventUpdate,
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    event_id: uuid.UUID,
) -> EventResponse:
    return await EventController(db).update(
        business_id, event_id, payload.model_dump(exclude_none=True)
    )
