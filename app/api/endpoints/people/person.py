from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import PersonController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import CrossBusinessPersonUser

router = APIRouter(tags=["people"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{person_id}", summary="Get a person by id")
async def get_person(
    db: DbSession,
    _: CrossBusinessPersonUser,
    person_id: uuid.UUID,
) -> Any:
    return await PersonController(db).get_by_id(person_id)


@router.patch("/{person_id}", summary="Update a person")
async def update_person(
    payload: dict[str, Any],
    db: DbSession,
    _: CrossBusinessPersonUser,
    person_id: uuid.UUID,
) -> Any:
    return await PersonController(db).update(person_id, payload)