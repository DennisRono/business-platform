from __future__ import annotations

import uuid
from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import PersonController
from business_platform.db.database import get_db
from business_platform.dependencies.authorization import CrossBusinessPersonUser

people_business_relationships_router = APIRouter(tags=["people"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@people_business_relationships_router.get("/{person_id}/business-relationships", summary="List person business relationships")
async def list_business_relationships(
    db: DbSession,
    _: CrossBusinessPersonUser,
    person_id: uuid.UUID,
) -> Any:
    return await PersonController(db).get_business_relationships(person_id)