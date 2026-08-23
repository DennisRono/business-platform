from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
)
from business_platform.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from business_platform.models.user import User
from business_platform.schemas.user import Token, UserCreate, UserUpdate
from business_platform.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


class UserController:
    """Encapsulates all user business logic and persistence."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Internal lookups ─────────────────────────────────────────────────────
    async def _get_active_or_none(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def _get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.username == username, User.is_deleted.is_(False)
            )
        )
        return result.scalar_one_or_none()

    # ── CRUD surface ──────────────────────────────────────────────────────────
    async def get_all(self, *, skip: int = 0, limit: int = DEFAULT_PAGE_SIZE) -> list[User]:
        """List non-deleted users, newest first, with bounded pagination."""
        limit = max(1, min(limit, MAX_PAGE_SIZE))
        result = await self.db.execute(
            select(User)
            .where(User.is_deleted.is_(False))
            .order_by(User.created_at.desc())
            .offset(max(skip, 0))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self._get_active_or_none(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} was not found.")
        return user

    async def create(self, payload: UserCreate) -> User:
        """Create a user, enforcing unique username/email before insert."""
        result = await self.db.execute(
            select(User).where(
                (User.username == payload.username) | (User.email == payload.email),
                User.is_deleted.is_(False),
            )
        )
        if result.scalar_one_or_none() is not None:
            raise ConflictError("A user with that username or email already exists.")

        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            role=payload.role,
            hashed_password=hash_password(payload.password),
        )
        self.db.add(user)
        await self.db.flush()  # assign PK / defaults without committing
        await self.db.refresh(user)
        return user

    async def update(self, user_id: uuid.UUID, payload: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        data = payload.model_dump(exclude_unset=True)

        if "password" in data:
            user.hashed_password = hash_password(data.pop("password"))
        for field, value in data.items():
            setattr(user, field, value)

        user.version += 1  # optimistic-concurrency bump
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: uuid.UUID) -> None:
        """SOFT delete: mark is_deleted + deleted_at, never remove the row."""
        user = await self.get_by_id(user_id)
        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)
        user.version += 1
        await self.db.flush()

    # ── Auth flows ────────────────────────────────────────────────────────────
    def _issue_tokens(self, user: User) -> Token:
        subject = {
            "sub": str(user.id),
            "username": user.username,
            "entity_id": str(user.id),
            "role": user.role.value,
        }
        return Token(
            access_token=create_access_token(subject),
            refresh_token=create_refresh_token(subject),
        )

    async def authenticate(self, username: str, password: str) -> Token:
        """Verify credentials and return an access/refresh token pair."""
        user = await self._get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Incorrect username or password.")
        if not user.is_active:
            raise AuthenticationError("This account is inactive.")
        return self._issue_tokens(user)
