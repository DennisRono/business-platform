from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import MembershipController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import BusinessOwnerOrAdminUser
from business_platform.schemas.membership import MembershipCreate, MembershipUpdate

businesses_memberships_router = APIRouter()

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@businesses_memberships_router.get("/{business_id}/memberships", summary="List business memberships")
async def list_memberships(
	db: DbSession,
	_: BusinessOwnerOrAdminUser,
	business_id: uuid.UUID,
) -> Any:
	return await MembershipController(db).get_all(business_id)


@businesses_memberships_router.post(
	"/{business_id}/memberships",
	status_code=status.HTTP_201_CREATED,
	summary="Create a membership",
)
async def create_membership(
	payload: MembershipCreate,
	db: DbSession,
	_: BusinessOwnerOrAdminUser,
	business_id: uuid.UUID,
) -> Any:
	return await MembershipController(db).create(business_id, payload.model_dump(exclude_none=True))


@businesses_memberships_router.patch("/{business_id}/memberships/{membership_id}", summary="Update a membership")
async def update_membership(
	payload: MembershipUpdate,
	db: DbSession,
	_: BusinessOwnerOrAdminUser,
	business_id: uuid.UUID,
	membership_id: uuid.UUID,
) -> Any:
	return await MembershipController(db).update(business_id, membership_id, payload.model_dump(exclude_none=True))
