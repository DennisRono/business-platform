from __future__ import annotations

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
from business_platform.models.tax import TaxIdentifier, TaxProfile
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.tax import (
    TaxIdentifierResponse,
    TaxProfileCreate,
    TaxProfileResponse,
)


class TaxController(_StubController):
    async def get_all(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[TaxProfileResponse]:
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
                .select_from(TaxProfile)
                .where(TaxProfile.business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(TaxProfile)
                .where(TaxProfile.business_id == business_id)
                .order_by(TaxProfile.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            profiles = result.scalars().all()

            items = [TaxProfileResponse.model_validate(profile) for profile in profiles]

            return PaginatedResponse[TaxProfileResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/taxes",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch tax profiles") from exc

    async def create(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> TaxProfileResponse:
        db = db or self.db

        try:
            tax_profile_create = TaxProfileCreate(**payload)

            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            existing_stmt = select(TaxProfile).where(
                TaxProfile.business_id == business_id,
                TaxProfile.jurisdiction == tax_profile_create.jurisdiction,
            )

            existing_result = await db.execute(existing_stmt)
            existing_profile = existing_result.scalar_one_or_none()

            if existing_profile:
                raise ConflictError(
                    message=(
                        f"A tax profile already exists for jurisdiction "
                        f"{tax_profile_create.jurisdiction!r} on business {business_id}"
                    )
                )

            tax_profile_data = tax_profile_create.model_dump(exclude_none=True)
            tax_profile_data["business_id"] = business_id

            new_profile = TaxProfile(**tax_profile_data)

            db.add(new_profile)

            await db.flush()
            await db.refresh(new_profile)

            return TaxProfileResponse.model_validate(new_profile)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Tax profile could not be created because "
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

            raise DatabaseError(message="Failed to create tax profile") from exc

    async def get_identifiers(
        self,
        business_id: UUID,
        tax_profile_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[TaxIdentifierResponse]:
        db = db or self.db

        try:
            profile_stmt = select(TaxProfile).where(
                TaxProfile.id == tax_profile_id,
                TaxProfile.business_id == business_id,
            )

            profile_result = await db.execute(profile_stmt)
            profile = profile_result.scalar_one_or_none()

            if not profile:
                raise NotFoundError(
                    message=(
                        f"Tax profile with ID {tax_profile_id} not found "
                        f"for business {business_id}"
                    )
                )

            offset = (page - 1) * size

            count_stmt = (
                select(func.count())
                .select_from(TaxIdentifier)
                .where(TaxIdentifier.tax_profile_id == tax_profile_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(TaxIdentifier)
                .where(TaxIdentifier.tax_profile_id == tax_profile_id)
                .order_by(TaxIdentifier.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            identifiers = result.scalars().all()

            items = [
                TaxIdentifierResponse.model_validate(identifier) for identifier in identifiers
            ]

            return PaginatedResponse[TaxIdentifierResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base
                or f"/businesses/{business_id}/taxes/{tax_profile_id}/identifiers",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch tax identifiers") from exc
