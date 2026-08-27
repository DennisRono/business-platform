"""User service — logic reusable outside the HTTP layer.

Services wrap controller operations for callers that are NOT an HTTP request,
e.g. background workers, seed scripts, or scheduled jobs. They own their own
``AsyncSession`` lifecycle (there is no ``get_db`` dependency in a worker) and
commit explicitly.
"""

from __future__ import annotations

from business_platform.controllers.auth.user import UserController
from business_platform.db.database import AsyncSessionLocal
from business_platform.models.user import User
from business_platform.schemas.user import UserCreate


class UserService:
    """Session-owning wrapper around :class:`UserController` for non-HTTP use."""

    async def create_user(self, payload: UserCreate) -> User:
        """Create a user from a background context, committing on success."""
        async with AsyncSessionLocal() as session:
            try:
                controller = UserController(session)
                user = await controller.create(payload)
                await session.commit()
                await session.refresh(user)
                return user
            except Exception:
                await session.rollback()
                raise
