from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import AuditLogController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import AuditLogAccessUser

audit_logs_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@audit_logs_router .get("/", summary="List audit logs")
async def list_audit_logs(
    db: DbSession,
    _: AuditLogAccessUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    actor_id: str | None = Query(default=None, description="Filter by actor id"),
    action: str | None = Query(default=None, description="Filter by action"),
    start_date: datetime | None = Query(default=None, description="Filter by start date"),
    end_date: datetime | None = Query(default=None, description="Filter by end date"),
) -> Any:
    return await AuditLogController(db).get_all(
        skip=skip,
        limit=limit,
        actor_id=actor_id,
        action=action,
        start_date=start_date,
        end_date=end_date,
    )