from __future__ import annotations

from typing import Annotated, Any, TypeAlias

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers import AuthController
from business_platform.db.database import get_db

router = APIRouter(tags=["auth"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Confirm a password reset",
)
async def confirm_password_reset(payload: dict[str, Any], db: DbSession) -> None:
    await AuthController(db).confirm_password_reset(payload)