from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import OwnershipController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessOwnerOrAdminUser

router = APIRouter(tags=["businesses"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{business_id}/owners", summary="List ownership records")
async def list_owners(
	db: DbSession,
	_: BusinessOwnerOrAdminUser,
	business_id: uuid.UUID,
) -> Any:
	return await OwnershipController(db).get_all(business_id)


@router.post(
	"/{business_id}/owners",
	status_code=status.HTTP_201_CREATED,
	summary="Create an ownership record",
)
async def create_owner(
	payload: dict[str, Any],
	db: DbSession,
	_: BusinessOwnerOrAdminUser,
	business_id: uuid.UUID,
) -> Any:
	return await OwnershipController(db).create(business_id, payload)


@router.patch(
	"/{business_id}/owners/{ownership_record_id}",
	summary="Transition an ownership record",
)
async def transition_owner(
	payload: dict[str, Any],
	db: DbSession,
	_: BusinessOwnerOrAdminUser,
	business_id: uuid.UUID,
	ownership_record_id: uuid.UUID,
) -> Any:
	return await OwnershipController(db).transition(business_id, ownership_record_id, payload)
