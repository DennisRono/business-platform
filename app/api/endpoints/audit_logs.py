from __future__ import annotations

from datetime import datetime
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import AuditLogController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import AuditLogAccessUser
from business_platform.schemas.audit_log import AuditLogResponse
from business_platform.schemas.base import PaginatedResponse
from business_platform.utils.constants import AUTH_RESPONSES
from business_platform.utils.pagination import PaginationQuery

audit_logs_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@audit_logs_router.get(
    "/",
    summary="List audit logs",
    responses=AUTH_RESPONSES,
    response_model=PaginatedResponse[AuditLogResponse],
)
async def list_audit_logs(
    db: DbSession,
    _: AuditLogAccessUser,
    pagination: PaginationQuery,
    actor_id: str | None = Query(default=None, description="Filter by actor id"),
    action: str | None = Query(default=None, description="Filter by action"),
    start_date: datetime | None = Query(default=None, description="Filter by start date"),
    end_date: datetime | None = Query(default=None, description="Filter by end date"),
) -> PaginatedResponse[AuditLogResponse]:
    return await AuditLogController(db).get_all(
        page=pagination.page,
        size=pagination.size,
        actor_id=actor_id,
        action=action,
        start_date=start_date,
        end_date=end_date,
        url_base="/audit-logs",
    )
