from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import LeadershipController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.leader import LeaderCreate

businesses_leaders_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_leaders_router.get("/{business_id}/leaders", summary="List leaders")
async def list_leaders(
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await LeadershipController(db).get_all(business_id)


@businesses_leaders_router.post(
	"/{business_id}/leaders",
	status_code=status.HTTP_201_CREATED,
	summary="Create a leader",
)
async def create_leader(
	payload: LeaderCreate,
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await LeadershipController(db).create(business_id, payload.model_dump(exclude_none=True))
