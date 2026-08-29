from __future__ import annotations

from decimal import Decimal
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
from business_platform.models.compensation import CompensationRecord
from business_platform.models.person import Person
from business_platform.schemas.aggregates import CompensationSummaryResponse
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.compensation import (
    CompensationRecordCreate,
    CompensationRecordResponse,
)


class CompensationController(_StubController):
    async def get_all(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[CompensationRecordResponse]:
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
                .select_from(CompensationRecord)
                .where(CompensationRecord.business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(CompensationRecord)
                .where(CompensationRecord.business_id == business_id)
                .order_by(CompensationRecord.effective_date.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            records = result.scalars().all()

            items = [CompensationRecordResponse.model_validate(record) for record in records]

            return PaginatedResponse[CompensationRecordResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/compensation",
            )

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch compensation records") from exc

    async def create(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> CompensationRecordResponse:
        db = db or self.db

        try:
            compensation_create = CompensationRecordCreate(**payload)

            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            person_stmt = select(Person).where(Person.id == compensation_create.person_id)

            person_result = await db.execute(person_stmt)
            person = person_result.scalar_one_or_none()

            if not person:
                raise NotFoundError(
                    message=f"Person with ID {compensation_create.person_id} not found"
                )

            compensation_data = compensation_create.model_dump(exclude_none=True)
            compensation_data["business_id"] = business_id

            new_record = CompensationRecord(**compensation_data)

            db.add(new_record)

            await db.flush()
            await db.refresh(new_record)

            return CompensationRecordResponse.model_validate(new_record)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Compensation record could not be created because "
                    "the supplied data conflicts with an existing record"
                )
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create compensation record") from exc

    async def get_history(
        self,
        business_id: UUID,
        person_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[CompensationRecordResponse]:
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
                .select_from(CompensationRecord)
                .where(
                    CompensationRecord.business_id == business_id,
                    CompensationRecord.person_id == person_id,
                )
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(CompensationRecord)
                .where(
                    CompensationRecord.business_id == business_id,
                    CompensationRecord.person_id == person_id,
                )
                .order_by(CompensationRecord.effective_date.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            records = result.scalars().all()

            items = [CompensationRecordResponse.model_validate(record) for record in records]

            return PaginatedResponse[CompensationRecordResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base
                or f"/businesses/{business_id}/compensation/{person_id}/history",
            )

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch compensation history") from exc

    async def summary(
        self,
        business_id: UUID,
        db: AsyncSession | None = None,
    ) -> CompensationSummaryResponse:
        db = db or self.db

        try:
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            stmt = select(CompensationRecord).where(
                CompensationRecord.business_id == business_id,
                CompensationRecord.is_current.is_(True),
            )

            result = await db.execute(stmt)
            current_records = result.scalars().all()

            currency = business.currency or (
                current_records[0].currency if current_records else "USD"
            )

            by_type: dict[Any, Decimal] = {}
            headcount_ids: set[UUID] = set()
            total = Decimal("0")

            for record in current_records:
                amount = Decimal(str(record.amount))
                by_type[record.compensation_type] = (
                    by_type.get(record.compensation_type, Decimal("0")) + amount
                )
                total += amount
                headcount_ids.add(record.person_id)

            return CompensationSummaryResponse(
                business_id=business_id,
                currency=currency,
                total_current_annualized=total,
                by_type=by_type,
                headcount_compensated=len(headcount_ids),
            )

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to summarize compensation") from exc
