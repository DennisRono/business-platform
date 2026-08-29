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
from business_platform.models.business import Business
from business_platform.models.person import Person
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.person import PersonCreate, PersonResponse


class BusinessPeopleController(_StubController):
    async def get_all(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[PersonResponse]:
        db = db or self.db

        try:
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            offset = (page - 1) * size

            count_stmt = (
                select(func.count())
                .select_from(Person)
                .where(Person.primary_business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(Person)
                .where(Person.primary_business_id == business_id)
                .order_by(Person.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            people = result.scalars().all()

            items = [PersonResponse.model_validate(person) for person in people]

            return PaginatedResponse[PersonResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/people",
            )

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch people") from exc

    async def create(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> PersonResponse:
        db = db or self.db

        try:
            person_create = PersonCreate(**payload)

            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            person_data = person_create.model_dump(exclude_none=True)
            person_data["primary_business_id"] = business_id

            new_person = Person(**person_data)

            db.add(new_person)

            await db.flush()
            await db.refresh(new_person)

            return PersonResponse.model_validate(new_person)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Person could not be created because "
                    "the supplied data conflicts with an existing record"
                )
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create person") from exc
