from __future__ import annotations

from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.user import UserController
from business_platform.db.database import get_db
from business_platform.schemas.user import LoginRequest, Token

router = APIRouter(tags=["auth"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.post("/login", response_model=Token, summary="Authenticate and get tokens")
async def login(payload: LoginRequest, db: DbSession) -> Token:
    return await UserController(db).authenticate(payload.username, payload.password)