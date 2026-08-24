from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import BusinessPeopleController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser

router = APIRouter(tags=["businesses"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{business_id}/people", summary="List people in a business")
async def list_people(
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await BusinessPeopleController(db).get_all(business_id)


@router.post(
	"/{business_id}/people",
	status_code=status.HTTP_201_CREATED,
	summary="Create a person within a business scope",
)
async def create_person(
	payload: dict[str, Any],
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await BusinessPeopleController(db).create(business_id, payload)
