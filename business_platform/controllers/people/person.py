from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DataError, IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.base import _StubController
from business_platform.core.exceptions import (
    BadRequestError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    NotFoundError,
)
from business_platform.models.business import Business
from business_platform.models.employee import Employee
from business_platform.models.leader import Leader
from business_platform.models.ownership import OwnershipRecord
from business_platform.models.person import Person
from business_platform.schemas.aggregates import PersonBusinessRelationshipResponse
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.person import PersonResponse, PersonUpdate


class PersonController(_StubController):
    async def get_by_id(
        self,
        person_id: UUID,
        db: AsyncSession | None = None,
    ) -> PersonResponse:
        db = db or self.db

        try:
            stmt = select(Person).where(Person.id == person_id)

            result = await db.execute(stmt)
            person = result.scalar_one_or_none()

            if not person:
                raise NotFoundError(message=f"Person with ID {person_id} not found")

            return PersonResponse.model_validate(person)

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="The request contains invalid data that could not be processed."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch person") from exc

    async def update(
        self,
        person_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> PersonResponse:
        db = db or self.db

        try:
            person_update = PersonUpdate(**payload)

            stmt = select(Person).where(Person.id == person_id)

            result = await db.execute(stmt)
            person = result.scalar_one_or_none()

            if not person:
                raise NotFoundError(message=f"Person with ID {person_id} not found")

            update_data = person_update.model_dump(exclude_none=True)

            for key, value in update_data.items():
                setattr(person, key, value)

            await db.flush()
            await db.refresh(person)

            return PersonResponse.model_validate(person)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Person could not be updated because "
                    "the supplied data conflicts with an existing record"
                )
            ) from exc

        except (DataError, OperationalError) as exc:
            await db.rollback()
            raise BadRequestError(
                message="The request contains invalid data that could not be processed."
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to update person") from exc

    async def get_business_relationships(
        self,
        person_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[PersonBusinessRelationshipResponse]:
        db = db or self.db

        try:
            person_stmt = select(Person).where(Person.id == person_id)

            person_result = await db.execute(person_stmt)
            person = person_result.scalar_one_or_none()

            if not person:
                raise NotFoundError(message=f"Person with ID {person_id} not found")

            ownership_result = await db.execute(
                select(OwnershipRecord).where(OwnershipRecord.person_id == person_id)
            )
            ownership_records = ownership_result.scalars().all()

            leader_result = await db.execute(
                select(Leader).where(Leader.person_id == person_id)
            )
            leader_records = leader_result.scalars().all()

            employee_result = await db.execute(
                select(Employee).where(Employee.person_id == person_id)
            )
            employee_records = employee_result.scalars().all()

            business_ids: set[UUID] = set()
            business_ids.update(record.business_id for record in ownership_records)
            business_ids.update(record.business_id for record in leader_records)
            business_ids.update(record.business_id for record in employee_records)

            if not business_ids:
                return PaginatedResponse[PersonBusinessRelationshipResponse].create(
                    items=[],
                    total=0,
                    page=page,
                    size=size,
                    url_base=url_base or f"/people/{person_id}/business-relationships",
                )

            businesses_result = await db.execute(
                select(Business).where(Business.id.in_(business_ids))
            )
            businesses_by_id = {
                business.id: business for business in businesses_result.scalars().all()
            }

            ownership_by_business = {record.business_id: record for record in ownership_records}
            leader_by_business = {record.business_id: record for record in leader_records}
            employee_by_business = {record.business_id: record for record in employee_records}

            relationships = []

            for business_id in business_ids:
                business = businesses_by_id.get(business_id)

                if not business:
                    continue

                ownership_record = ownership_by_business.get(business_id)
                leader_record = leader_by_business.get(business_id)
                employee_record = employee_by_business.get(business_id)

                relationships.append(
                    PersonBusinessRelationshipResponse(
                        business_id=business_id,
                        business_name=business.name,
                        is_owner=ownership_record is not None,
                        ownership_type=ownership_record.ownership_type
                        if ownership_record
                        else None,
                        ownership_percentage=ownership_record.percentage
                        if ownership_record
                        else None,
                        is_leader=leader_record is not None,
                        leader_title=leader_record.title if leader_record else None,
                        is_employee=employee_record is not None,
                        employment_status=employee_record.employment_status
                        if employee_record
                        else None,
                        job_title=employee_record.job_title if employee_record else None,
                    )
                )

            relationships.sort(key=lambda item: item.business_name)

            total = len(relationships)
            offset = (page - 1) * size
            page_items = relationships[offset : offset + size]

            return PaginatedResponse[PersonBusinessRelationshipResponse].create(
                items=page_items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/people/{person_id}/business-relationships",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch person business relationships") from exc
