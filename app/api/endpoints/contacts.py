from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import ContactController
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser

router = APIRouter(prefix="/contacts", tags=["contacts"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", summary="List contacts")
async def list_contacts(
    db: DbSession,
    _: GetCurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    return await ContactController(db).get_all(skip=skip, limit=limit)


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a contact")
async def create_contact(payload: dict[str, Any], db: DbSession, _: GetCurrentUser) -> Any:
    return await ContactController(db).create(payload)


@router.get("/{contact_id}", summary="Get a contact by id")
async def get_contact(
    db: DbSession,
    _: GetCurrentUser,
    contact_id: uuid.UUID,
) -> Any:
    return await ContactController(db).get_by_id(contact_id)