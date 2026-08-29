from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
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
from business_platform.models.ownership import OwnershipRecord, OwnershipTransition
from business_platform.models.person import Person
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.ownership import (
    OwnershipRecordCreate,
    OwnershipRecordResponse,
    OwnershipTransitionRequest,
)


class OwnershipController(_StubController):
    async def get_all(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[OwnershipRecordResponse]:
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
                .select_from(OwnershipRecord)
                .where(OwnershipRecord.business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(OwnershipRecord)
                .where(OwnershipRecord.business_id == business_id)
                .order_by(OwnershipRecord.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            records = result.scalars().all()

            items = [OwnershipRecordResponse.model_validate(record) for record in records]

            return PaginatedResponse[OwnershipRecordResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/owners",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch ownership records") from exc

    async def create(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> OwnershipRecordResponse:
        db = db or self.db

        try:
            ownership_create = OwnershipRecordCreate(**payload)

            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            person_stmt = select(Person).where(Person.id == ownership_create.person_id)

            person_result = await db.execute(person_stmt)
            person = person_result.scalar_one_or_none()

            if not person:
                raise NotFoundError(
                    message=f"Person with ID {ownership_create.person_id} not found"
                )

            ownership_data = ownership_create.model_dump(exclude_none=True)
            ownership_data["business_id"] = business_id

            new_record = OwnershipRecord(**ownership_data)

            db.add(new_record)

            await db.flush()
            await db.refresh(new_record)

            return OwnershipRecordResponse.model_validate(new_record)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Ownership record could not be created because "
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

            raise DatabaseError(message="Failed to create ownership record") from exc

    async def transition(
        self,
        business_id: UUID,
        ownership_record_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
        transitioned_by_id: UUID | None = None,
    ) -> OwnershipRecordResponse:
        db = db or self.db

        try:
            transition_request = OwnershipTransitionRequest(**payload)

            stmt = select(OwnershipRecord).where(
                OwnershipRecord.id == ownership_record_id,
                OwnershipRecord.business_id == business_id,
            )

            result = await db.execute(stmt)
            record = result.scalar_one_or_none()

            if not record:
                raise NotFoundError(
                    message=(
                        f"Ownership record with ID {ownership_record_id} "
                        f"not found for business {business_id}"
                    )
                )

            if record.status == transition_request.to_status:
                raise BusinessLogicError(
                    message=f"Ownership record is already in status {transition_request.to_status}"
                )

            from_status = record.status

            record.status = transition_request.to_status

            transition_log = OwnershipTransition(
                ownership_record_id=record.id,
                from_status=from_status,
                to_status=transition_request.to_status,
                transitioned_at=datetime.now(timezone.utc),
                transitioned_by_id=transitioned_by_id,
                reason=transition_request.reason,
            )

            db.add(transition_log)

            await db.flush()
            await db.refresh(record)

            return OwnershipRecordResponse.model_validate(record)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except (DataError, OperationalError) as exc:
            await db.rollback()
            raise BadRequestError(
                message="The request contains invalid data that could not be processed."
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to transition ownership record") from exc
