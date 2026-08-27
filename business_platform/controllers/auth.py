from __future__ import annotations

import uuid
from typing import Any

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.core.exceptions import (
    AuthenticationError,
    BusinessLogicError,
    DatabaseError,
    NotFoundError,
)

from business_platform.core.security import (
    JWTError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from business_platform.models.user import User
from business_platform.schemas.user import Token, UserCreate, UserResponse
from business_platform.utils.enums import TokenType


class AuthController:
    async def register_user(self, payload: dict[str, Any], db: AsyncSession) -> Token:
        """Register a new user and return access/refresh tokens."""
        try:
            user_data = UserCreate(**payload)

            existing_by_username = await db.execute(
                select(User).where(User.username == user_data.username)
            )
            if existing_by_username.scalars().first():
                raise BusinessLogicError(message="Username already exists")

            existing_by_email = await db.execute(
                select(User).where(User.email == user_data.email)
            )
            if existing_by_email.scalars().first():
                raise BusinessLogicError(message="Email already exists")

            user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                role=user_data.role,
                hashed_password=hash_password(user_data.password),
                is_active=True,
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            subject = {
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.value
            }

            
            return Token(
                access_token=create_access_token(subject),
                refresh_token=create_refresh_token(subject),
                token_type="bearer",
            )

        except SQLAlchemyError as exc:
            await db.rollback()
            
            raise DatabaseError(message="Failed to register user") from exc
        except Exception:
            await db.rollback()
            raise

    async def login(self, form_data: OAuth2PasswordRequestForm, db: AsyncSession) -> Token:
        """Authenticate user and return access/refresh tokens."""
        try:
            result = await db.execute(
                select(User).where(User.username == form_data.username)
            )
            user = result.scalars().one_or_none()

            if not user:
                raise AuthenticationError(message="Invalid username or password")

            if not user.is_active:
                raise AuthenticationError(message="User account is inactive")

            if not verify_password(form_data.password, user.hashed_password):
                raise AuthenticationError(message="Invalid username or password")

            subject = {
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.value,
                "entity_id": None,
            }

            
            return Token(
                access_token=create_access_token(subject),
                refresh_token=create_refresh_token(subject),
                token_type="bearer",
            )

        except SQLAlchemyError as exc:
            await db.rollback()
            
            raise DatabaseError(message="Login failed due to database error") from exc

    async def logout(self, current_user: Any, db: AsyncSession) -> dict[str, str]:
        """Stateless logout: client should discard its tokens."""
        
        return {"message": "Successfully logged out"}

    async def refresh_token(self, refresh_token: str, db: AsyncSession) -> Token:
        """Mint a new token pair from a valid refresh token."""
        try:
            payload = decode_token(refresh_token)
        except JWTError as exc:
            raise AuthenticationError(message="Invalid refresh token") from exc

        if payload.get("type") != TokenType.REFRESH.value:
            raise AuthenticationError(message="Refresh token required")

        sub = payload.get("sub")
        if not sub:
            raise AuthenticationError(message="Invalid refresh token")

        try:
            user_id = uuid.UUID(str(sub))
        except ValueError as exc:
            raise AuthenticationError(message="Invalid refresh token") from exc

        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().one_or_none()

            if not user or not user.is_active:
                raise AuthenticationError(message="User not found or inactive")

            subject = {
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.value,
                "entity_id": None,
            }

            return Token(
                access_token=create_access_token(subject),
                refresh_token=create_refresh_token(subject),
                token_type="bearer",
            )

        except SQLAlchemyError as exc:
            
            raise DatabaseError(message="Token refresh failed due to database error") from exc

    async def me(self, current_user: Any, db: AsyncSession) -> UserResponse:
        """Return the current authenticated user profile."""
        try:
            result = await db.execute(select(User).where(User.id == current_user.sub))
            user = result.scalars().one_or_none()

            if not user:
                raise NotFoundError(message="User not found")

            return UserResponse.model_validate(user)

        except SQLAlchemyError as exc:
            
            raise DatabaseError(message="Failed to fetch user profile") from exc