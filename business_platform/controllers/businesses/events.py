from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import DataError, IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.base import _StubController
from business_platform.core.exceptions import (
    BadRequestError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    NotFoundError,
)
from business_platform.models.business import Business
from business_platform.models.event import Event
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.event import EventCreate, EventResponse, EventUpdate


class EventController(_StubController):
    async def get_all(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        event_type: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[EventResponse]:
        db = db or self.db

        try:
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            filters = [Event.business_id == business_id]

            if event_type:
                filters.append(Event.event_type == event_type)

            if status:
                filters.append(Event.status == status)

            if start_date:
                filters.append(Event.start_date >= start_date)

            if end_date:
                filters.append(Event.start_date <= end_date)

            offset = (page - 1) * size

            count_stmt = select(func.count()).select_from(Event).where(*filters)

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(Event)
                .where(*filters)
                .order_by(Event.start_date.asc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            events = result.scalars().all()

            items = [EventResponse.model_validate(event) for event in events]

            return PaginatedResponse[EventResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/events",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch events") from exc

    async def create(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> EventResponse:
        db = db or self.db

        try:
            event_create = EventCreate(**payload)

            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            event_data = event_create.model_dump(exclude_none=True)
            event_data["business_id"] = business_id

            new_event = Event(**event_data)

            db.add(new_event)

            await db.flush()
            await db.refresh(new_event)

            return EventResponse.model_validate(new_event)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Event could not be created because "
                    "the supplied data conflicts with an existing record"
                )
            ) from exc

        except (DataError, OperationalError) as exc:
            await db.rollback()
            raise BadRequestError(
                message="The request contains invalid data that could not be processed."
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create event") from exc

    async def update(
        self,
        business_id: UUID,
        event_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> EventResponse:
        db = db or self.db

        try:
            event_update = EventUpdate(**payload)

            stmt = select(Event).where(
                Event.id == event_id,
                Event.business_id == business_id,
            )

            result = await db.execute(stmt)
            event = result.scalar_one_or_none()

            if not event:
                raise NotFoundError(
                    message=f"Event with ID {event_id} not found for business {business_id}"
                )

            update_data = event_update.model_dump(exclude_none=True)

            for key, value in update_data.items():
                setattr(event, key, value)

            await db.flush()
            await db.refresh(event)

            return EventResponse.model_validate(event)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Event could not be updated because "
                    "the supplied data conflicts with an existing record"
                )
            ) from exc

        except (DataError, OperationalError) as exc:
            await db.rollback()
            raise BadRequestError(
                message="The request contains invalid data that could not be processed."
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to update event") from exc
