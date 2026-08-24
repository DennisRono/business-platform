from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import LeadershipController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser

router = APIRouter(tags=["businesses"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{business_id}/leaders", summary="List leaders")
async def list_leaders(
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await LeadershipController(db).get_all(business_id)


@router.post(
	"/{business_id}/leaders",
	status_code=status.HTTP_201_CREATED,
	summary="Create a leader",
)
async def create_leader(
	payload: dict[str, Any],
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await LeadershipController(db).create(business_id, payload)
