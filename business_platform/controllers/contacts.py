from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.base import _StubController
from business_platform.core.exceptions import (
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    NotFoundError,
)
from business_platform.models.contact import Contact
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.contact import ContactCreate, ContactResponse


class ContactController(_StubController):
    async def get_all(
        self,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[ContactResponse]:
        db = db or self.db

        try:
            offset = (page - 1) * size

            count_stmt = select(func.count()).select_from(Contact)

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(Contact)
                .order_by(Contact.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            contacts = result.scalars().all()

            items = [ContactResponse.model_validate(contact) for contact in contacts]

            return PaginatedResponse[ContactResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or "/contacts",
            )

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch contacts") from exc

    async def create(
        self,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> ContactResponse:
        db = db or self.db

        try:
            contact_create = ContactCreate(**payload)

            new_contact = Contact(**contact_create.model_dump(exclude_none=True))

            db.add(new_contact)

            await db.flush()
            await db.refresh(new_contact)

            return ContactResponse.model_validate(new_contact)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Contact could not be created because "
                    "the supplied data conflicts with an existing record"
                )
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create contact") from exc

    async def get_by_id(
        self,
        contact_id: UUID,
        db: AsyncSession | None = None,
    ) -> ContactResponse:
        db = db or self.db

        try:
            stmt = select(Contact).where(Contact.id == contact_id)

            result = await db.execute(stmt)
            contact = result.scalar_one_or_none()

            if not contact:
                raise NotFoundError(message=f"Contact with ID {contact_id} not found")

            return ContactResponse.model_validate(contact)

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch contact") from exc
