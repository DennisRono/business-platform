from __future__ import annotations

from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import AuthController
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser

router = APIRouter(tags=["auth"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="End the current session")
async def logout(
    current_user: GetCurrentUser,
    db: DbSession,
    payload: dict[str, Any] | None = None,
) -> None:
    await AuthController(db).logout(current_user, payload)