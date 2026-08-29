from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.auth import AuthController
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser
from business_platform.schemas.user import RefreshRequest, Token, UserCreate, UserResponse
from business_platform.utils.constants import AUTH_RESPONSES

auth_router = APIRouter()
auth_controller = AuthController()


@auth_router.post(
    "/register", status_code=status.HTTP_201_CREATED, responses=AUTH_RESPONSES, response_model=Token
)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    return await auth_controller.register_user(payload=payload, db=db)


@auth_router.post(
    "/login", status_code=status.HTTP_200_OK, responses=AUTH_RESPONSES, response_model=Token
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    return await auth_controller.login(form_data=form_data, db=db)


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: GetCurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await auth_controller.logout(current_user=current_user, db=db)


@auth_router.post("/token/refresh", responses=AUTH_RESPONSES, response_model=Token)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    return await auth_controller.refresh_token(refresh_token=payload.refresh_token, db=db)


@auth_router.get("/me", responses=AUTH_RESPONSES, response_model=UserResponse)
async def me(current_user: GetCurrentUser, db: AsyncSession = Depends(get_db)):
    return await auth_controller.me(current_user=current_user, db=db)
