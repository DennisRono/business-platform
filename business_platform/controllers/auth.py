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
from business_platform.schemas.user import (
    RefreshRequest,
    Token,
    UserCreate,
    UserResponse,
)
from business_platform.utils.enums import TokenType


class AuthController:
    async def register_user(
        self,
        payload: UserCreate,
        db: AsyncSession,
    ) -> Token:
        """Register a new user and return access/refresh tokens."""
        try:
            
            result = await db.execute(
                select(User).where(
                    (User.username == payload.username) | (User.email == payload.email)
                )
            )
            existing_user = result.scalars().first()

            if existing_user:
                if existing_user.username == payload.username:
                    raise BusinessLogicError(message="Username already registered")

                raise BusinessLogicError(message="Email already registered")

            user = User(
                username=payload.username,
                email=str(payload.email),
                full_name=payload.full_name,
                role=payload.role,
                hashed_password=hash_password(payload.password),
                is_active=True,
            )

            db.add(user)
            await db.flush()

            subject = {
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.value,
                "entity_id": None,
            }

            access_token = create_access_token(subject)
            refresh_token = create_refresh_token(subject)

            await db.commit()

            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )

        except SQLAlchemyError as exc:
            await db.rollback()
            raise DatabaseError(message="Failed to register user") from exc

        except Exception:
            await db.rollback()
            raise

    async def login(
        self,
        form_data: OAuth2PasswordRequestForm,
        db: AsyncSession,
    ) -> Token:
        """Authenticate user and return access/refresh tokens."""
        try:
            result = await db.execute(select(User).where(User.username == form_data.username))
            user = result.scalars().one_or_none()

            
            
            if not user or not verify_password(
                form_data.password,
                user.hashed_password,
            ):
                raise AuthenticationError(message="Invalid username or password")

            if not user.is_active:
                raise AuthenticationError(message="User account is inactive")

            subject = {
                "sub": str(user.id),
                "username": user.username,
                "role": user.role,
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

    async def logout(
        self,
        current_user: Any,
        db: AsyncSession,
    ) -> dict[str, str]:
        """Stateless logout: client should discard its tokens."""
        return {"message": "Successfully logged out"}

    async def refresh_token(
        self,
        refresh_token: str,
        db: AsyncSession,
    ) -> Token:
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
        except (ValueError, AttributeError, TypeError) as exc:
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
            await db.rollback()
            raise DatabaseError(message="Token refresh failed due to database error") from exc

    async def me(
        self,
        current_user: Any,
        db: AsyncSession,
    ) -> UserResponse:
        """Return the current authenticated user profile."""
        try:
            result = await db.execute(select(User).where(User.id == current_user.sub))
            user = result.scalars().one_or_none()

            if not user:
                raise NotFoundError(message="User not found")

            return UserResponse.model_validate(user)

        except SQLAlchemyError as exc:
            await db.rollback()
            raise DatabaseError(message="Failed to fetch user profile") from exc
