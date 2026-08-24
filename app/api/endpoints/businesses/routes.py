from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import BusinessController
from business_platform.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser
from business_platform.dependencies.authorization import (
	BusinessAccessUser,
	BusinessOwnerOrAdminUser,
)

from .compensation import router as compensation_router
from .documents import router as documents_router
from .employees import router as employees_router
from .events import router as events_router
from .financials import router as financials_router
from .leaders import router as leaders_router
from .memberships import router as memberships_router
from .owners import router as owners_router
from .people import router as business_people_router
from .relationships import router as relationships_router
from .taxes import router as taxes_router
from .tasks import router as tasks_router

router = APIRouter(prefix="/businesses", tags=["businesses"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


# ── Business root ───────────────────────────────────────────────────────────
@router.get("/", summary="List businesses")
async def list_businesses(
	db: DbSession,
	_: BusinessAccessUser,
	skip: int = Query(0, ge=0),
	limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> Any:
	return await BusinessController(db).get_all(skip=skip, limit=limit)


@router.post(
	"/",
	status_code=status.HTTP_201_CREATED,
	summary="Create a business",
)
async def create_business(payload: dict[str, Any], db: DbSession, _: GetCurrentUser) -> Any:
	return await BusinessController(db).create(payload)


@router.get("/{business_id}", summary="Get a business by id")
async def get_business(
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await BusinessController(db).get_by_id(business_id)


@router.patch("/{business_id}", summary="Update a business")
async def update_business(
	payload: dict[str, Any],
	db: DbSession,
	_: BusinessAccessUser,
	business_id: uuid.UUID,
) -> Any:
	return await BusinessController(db).update(business_id, payload)


@router.delete(
	"/{business_id}",
	status_code=status.HTTP_204_NO_CONTENT,
	summary="Soft-delete a business",
)
async def delete_business(
	db: DbSession,
	_: BusinessOwnerOrAdminUser,
	business_id: uuid.UUID,
) -> None:
	await BusinessController(db).delete(business_id)


# Re-export subresource routers under the /businesses prefix.
router.include_router(relationships_router)
router.include_router(memberships_router)
router.include_router(business_people_router)
router.include_router(owners_router)
router.include_router(leaders_router)
router.include_router(employees_router)
router.include_router(compensation_router)
router.include_router(taxes_router)
router.include_router(documents_router)
router.include_router(events_router)
router.include_router(tasks_router)
router.include_router(financials_router)
