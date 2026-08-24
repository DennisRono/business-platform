from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import EventController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser

router = APIRouter(tags=["businesses"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{business_id}/events", summary="List events")
async def list_events(
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    event_type: str | None = Query(default=None, description="Filter by event type"),
    event_status: str | None = Query(default=None, alias="status", description="Filter by status"),
    start_date: datetime | None = Query(default=None, description="Filter by start date"),
    end_date: datetime | None = Query(default=None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    return await EventController(db).get_all(
        business_id,
        event_type=event_type,
        status=event_status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{business_id}/events",
    status_code=status.HTTP_201_CREATED,
    summary="Create an event",
)
async def create_event(
    payload: dict[str, Any],
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
) -> Any:
    return await EventController(db).create(business_id, payload)


@router.patch("/{business_id}/events/{event_id}", summary="Update an event")
async def update_event(
    payload: dict[str, Any],
    db: DbSession,
    _: BusinessAccessUser,
    business_id: uuid.UUID,
    event_id: uuid.UUID,
) -> Any:
    return await EventController(db).update(business_id, event_id, payload)