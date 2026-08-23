from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.user import UserController
from business_platform.core.security import JWTError, create_access_token, decode_token
from business_platform.db.database import get_db
from business_platform.dependencies.auth import GetCurrentUser
from business_platform.core.exceptions import AuthenticationError
from business_platform.schemas.user import (
    LoginRequest,
    RefreshRequest,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from business_platform.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from business_platform.utils.enums import TokenType

router = APIRouter(prefix="/users", tags=["users"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


# ── Auth flows ────────────────────────────────────────────────────────────────
@router.post("/login", response_model=Token, summary="Authenticate and get tokens")
async def login(payload: LoginRequest, db: DbSession) -> Token:
    return await UserController(db).authenticate(payload.username, payload.password)


@router.post("/refresh", response_model=Token, summary="Mint a new access token")
async def refresh(payload: RefreshRequest, db: DbSession) -> Token:
    try:
        claims = decode_token(payload.refresh_token)
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired refresh token.") from exc

    if claims.get("type") != TokenType.REFRESH.value:
        raise AuthenticationError("An access token cannot be used to refresh.")

    subject = {
        "sub": claims["sub"],
        "username": claims["username"],
        "entity_id": claims.get("entity_id"),
        "role": claims["role"],
    }
    return Token(
        access_token=create_access_token(subject),
        refresh_token=payload.refresh_token,
    )


@router.get("/me", response_model=UserResponse, summary="Current authenticated user")
async def read_me(current_user: GetCurrentUser, db: DbSession) -> UserResponse:
    user = await UserController(db).get_by_id(current_user.sub)
    return UserResponse.model_validate(user)


# ── Fixed CRUD surface ─────────────────────────────────────────────────────────
@router.get("/", response_model=list[UserResponse], summary="List users")
async def list_users(
    db: DbSession,
    _: GetCurrentUser,
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
async def create_user(payload: UserCreate, db: DbSession) -> UserResponse:
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
    _: GetCurrentUser,
) -> UserResponse:
    user = await UserController(db).update(user_id, payload)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a user",
)
async def delete_user(user_id: uuid.UUID, db: DbSession, _: GetCurrentUser) -> None:
    await UserController(db).delete(user_id)
