from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import LeadershipController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.leader import LeaderCreate, LeaderResponse
from business_platform.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

businesses_leaders_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_leaders_router.get(
	"/{business_id}/leaders",
	summary="List leaders",
	response_model=PaginatedResponse[LeaderResponse],
)
async def list_leaders(
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
	page: int = Query(1, ge=1),
	size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[LeaderResponse]:
	return await LeadershipController(db).get_all(
		business_id,
		page=page,
		size=size,
		url_base=f"/businesses/{business_id}/leaders",
	)


@businesses_leaders_router.post(
	"/{business_id}/leaders",
	status_code=status.HTTP_201_CREATED,
	summary="Create a leader",
	response_model=LeaderResponse,
)
async def create_leader(
	payload: LeaderCreate,
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> LeaderResponse:
	return await LeadershipController(db).create(business_id, payload.model_dump(exclude_none=True))
