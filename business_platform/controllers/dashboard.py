from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.base import _StubController
from business_platform.core.exceptions import DatabaseError
from business_platform.models.business import Business
from business_platform.models.employee import Employee
from business_platform.models.event import Event
from business_platform.models.ownership import OwnershipRecord
from business_platform.models.person import Person
from business_platform.models.task import Task
from business_platform.schemas.aggregates import (
    DashboardOverviewResponse,
    UpcomingItemResponse,
)
from business_platform.schemas.base import PaginatedResponse
from business_platform.utils.enums import BusinessStatus, OwnershipStatus, TaskStatus


class DashboardController(_StubController):
    async def overview(
        self,
        db: AsyncSession | None = None,
    ) -> DashboardOverviewResponse:
        db = db or self.db

        try:
            total_businesses = (
                await db.execute(select(func.count()).select_from(Business))
            ).scalar_one()

            active_businesses = (
                await db.execute(
                    select(func.count())
                    .select_from(Business)
                    .where(Business.status == BusinessStatus.ACTIVE)
                )
            ).scalar_one()

            total_people = (
                await db.execute(select(func.count()).select_from(Person))
            ).scalar_one()

            total_employees = (
                await db.execute(select(func.count()).select_from(Employee))
            ).scalar_one()

            open_tasks = (
                await db.execute(
                    select(func.count())
                    .select_from(Task)
                    .where(Task.status != TaskStatus.COMPLETED)
                )
            ).scalar_one()

            now = datetime.now(timezone.utc)

            upcoming_events_count = (
                await db.execute(
                    select(func.count())
                    .select_from(Event)
                    .where(Event.start_date >= now)
                )
            ).scalar_one()

            pending_ownership_transitions = (
                await db.execute(
                    select(func.count())
                    .select_from(OwnershipRecord)
                    .where(OwnershipRecord.status == OwnershipStatus.PENDING)
                )
            ).scalar_one()

            return DashboardOverviewResponse(
                total_businesses=total_businesses,
                active_businesses=active_businesses,
                total_people=total_people,
                total_employees=total_employees,
                open_tasks=open_tasks,
                upcoming_events_count=upcoming_events_count,
                pending_ownership_transitions=pending_ownership_transitions,
            )

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch dashboard overview") from exc

    async def upcoming(
        self,
        page: int = 1,
        size: int = 20,
        days_ahead: int = 30,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[UpcomingItemResponse]:
        db = db or self.db

        try:
            now = datetime.now(timezone.utc)
            horizon = now + timedelta(days=days_ahead)

            events_result = await db.execute(
                select(Event).where(
                    Event.start_date >= now,
                    Event.start_date <= horizon,
                )
            )
            events = events_result.scalars().all()

            tasks_result = await db.execute(
                select(Task).where(
                    Task.due_date.is_not(None),
                    Task.due_date >= now,
                    Task.due_date <= horizon,
                    Task.status != TaskStatus.COMPLETED,
                )
            )
            tasks = tasks_result.scalars().all()

            combined = [
                UpcomingItemResponse(
                    item_type="event",
                    id=event.id,
                    business_id=event.business_id,
                    title=event.title,
                    due_at=event.start_date,
                )
                for event in events
            ] + [
                UpcomingItemResponse(
                    item_type="task",
                    id=task.id,
                    business_id=task.business_id,
                    title=task.title,
                    due_at=task.due_date,
                )
                for task in tasks
            ]

            combined.sort(key=lambda item: item.due_at)

            total = len(combined)
            offset = (page - 1) * size
            page_items = combined[offset : offset + size]

            return PaginatedResponse[UpcomingItemResponse].create(
                items=page_items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or "/dashboard/upcoming",
            )

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch upcoming items") from exc
