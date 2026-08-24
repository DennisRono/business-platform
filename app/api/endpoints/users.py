from __future__ import annotations

import uuid
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.user import UserController
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser
from business_platform.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from business_platform.dependencies.authorization import (
    SystemAdminUser,
    UserUpdateAccessUser,
)
from business_platform.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter(prefix="/users", tags=["users"])

DbSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]


@router.get("/me", response_model=UserResponse, summary="Current authenticated user")
async def read_me(current_user: GetCurrentUser, db: DbSession) -> UserResponse:
    user = await UserController(db).get_by_id(current_user.sub)
    return UserResponse.model_validate(user)


# ── Fixed CRUD surface ─────────────────────────────────────────────────────────
@router.get("/", response_model=list[UserResponse], summary="List users")
async def list_users(
    db: DbSession,
    _: SystemAdminUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> list[UserResponse]:
    users = await UserController(db).get_all(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
async def create_user(payload: UserCreate, db: DbSession, _: SystemAdminUser) -> UserResponse:
    user = await UserController(db).create(payload)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse, summary="Get a user by id")
async def get_user(user_id: uuid.UUID, db: DbSession, _: GetCurrentUser) -> UserResponse:
    user = await UserController(db).get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse, summary="Update a user")
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: DbSession,
    _: UserUpdateAccessUser,
) -> UserResponse:
    user = await UserController(db).update(user_id, payload)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a user",
)
async def delete_user(user_id: uuid.UUID, db: DbSession, _: SystemAdminUser) -> None:
    await UserController(db).delete(user_id)
