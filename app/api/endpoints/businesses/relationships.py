from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import BusinessController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessAccessUser
from business_platform.schemas.business_relationship import BusinessRelationshipCreate

businesses_relationships_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_relationships_router.get("/{business_id}/relationships", summary="List business relationships")
async def list_relationships(
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await BusinessController(db).get_relationships(business_id)


@businesses_relationships_router.post(
	"/{business_id}/relationships",
	status_code=status.HTTP_201_CREATED,
	summary="Create a business relationship",
)
async def create_relationship(
	payload: BusinessRelationshipCreate,
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await BusinessController(db).create_relationship(business_id, payload.model_dump(exclude_none=True))
