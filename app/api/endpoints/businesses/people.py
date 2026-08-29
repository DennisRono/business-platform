from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import BusinessPeopleController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.person import PersonCreate

businesses_people_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_people_router.get("/{business_id}/people", summary="List people in a business")
async def list_people(
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await BusinessPeopleController(db).get_all(business_id)


@businesses_people_router.post(
	"/{business_id}/people",
	status_code=status.HTTP_201_CREATED,
	summary="Create a person within a business scope",
)
async def create_person(
	payload: PersonCreate,
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await BusinessPeopleController(db).create(business_id, payload.model_dump(exclude_none=True))
