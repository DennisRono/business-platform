from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import DataError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.base import _StubController
from business_platform.core.exceptions import BadRequestError, DatabaseError
from business_platform.models.audit_log import AuditLog
from business_platform.schemas.audit_log import AuditLogResponse
from business_platform.schemas.base import PaginatedResponse


class AuditLogController(_StubController):
    async def get_all(
        self,
        page: int = 1,
        size: int = 20,
        actor_id: str | None = None,
        action: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[AuditLogResponse]:
        db = db or self.db

        try:
            filters = []

            if actor_id:
                try:
                    filters.append(AuditLog.actor_id == UUID(actor_id))
                except ValueError:
                    filters.append(AuditLog.actor_id == None)  # noqa: E711

            if action:
                filters.append(AuditLog.action == action)

            if start_date:
                filters.append(AuditLog.created_at >= start_date)

            if end_date:
                filters.append(AuditLog.created_at <= end_date)

            offset = (page - 1) * size

            count_stmt = select(func.count()).select_from(AuditLog).where(*filters)

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(AuditLog)
                .where(*filters)
                .order_by(AuditLog.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            audit_logs = result.scalars().all()

            items = [AuditLogResponse.model_validate(log) for log in audit_logs]

            return PaginatedResponse[AuditLogResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or "/audit-logs",
            )

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc
        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch audit logs") from exc
