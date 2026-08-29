from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.base import _StubController
from business_platform.core.exceptions import (
    AuthorizationError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    NotFoundError,
)



class BusinessController(_StubController):

    async def get_all(
        self,
        current_user: Any,
        skip: int = 0,
        limit: int = 20,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        db: AsyncSession | None = None,
    ):
        db = db or self.db

        try:
            if current_user.role not in {"admin", "manager"}:
                raise AuthorizationError(message="Not authorized to list businesses")


        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch businesses") from exc

    async def create(
        self,
        payload: dict[str, Any],
        current_user: Any,
        db: AsyncSession | None = None,
    ):
        db = db or self.db

        try:
            pass

        except BusinessLogicError:
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message="Business could not be created because "
                "the supplied data conflicts with an existing record"
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create business") from exc

    async def get_by_id(
        self,
        business_id: UUID,
        db: AsyncSession | None = None,
    ):
        db = db or self.db

        try:
            pass

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch business") from exc

    async def update(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ):
        db = db or self.db

        try:
            pass

        except NotFoundError:
            await db.rollback()
            raise

        except BusinessLogicError:
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message="Business could not be updated because "
                "the supplied data conflicts with an existing record"
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to update business") from exc

    async def delete(
        self,
        business_id: UUID,
        db: AsyncSession | None = None,
    ) -> None:
        db = db or self.db

        try:
            pass

        except NotFoundError:
            await db.rollback()
            raise

        except BusinessLogicError:
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(message="Business could not be deleted") from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to delete business") from exc

    async def get_relationships(
        self,
        business_id: UUID,
        db: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        db = db or self.db

        try:
            pass
        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch business relationships") from exc

    async def create_relationship(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        db = db or self.db

        try:
            pass

        except (
            NotFoundError,
            BusinessLogicError,
            ConflictError,
        ):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message="The ownership relationship conflicts " "with existing data"
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create business relationship") from exc
