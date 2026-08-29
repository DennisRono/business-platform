from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import BusinessPeopleController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.person import PersonCreate, PersonResponse
from business_platform.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

businesses_people_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_people_router.get(
	"/{business_id}/people",
	summary="List people in a business",
	response_model=PaginatedResponse[PersonResponse],
)
async def list_people(
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
	page: int = Query(1, ge=1),
	size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse[PersonResponse]:
	return await BusinessPeopleController(db).get_all(
		business_id,
		page=page,
		size=size,
		url_base=f"/businesses/{business_id}/people",
	)


@businesses_people_router.post(
	"/{business_id}/people",
	status_code=status.HTTP_201_CREATED,
	summary="Create a person within a business scope",
	response_model=PersonResponse,
)
async def create_person(
	payload: PersonCreate,
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> PersonResponse:
	return await BusinessPeopleController(db).create(business_id, payload.model_dump(exclude_none=True))
