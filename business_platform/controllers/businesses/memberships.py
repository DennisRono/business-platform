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
from business_platform.models.membership import Membership
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.membership import (
    MembershipCreate,
    MembershipResponse,
    MembershipUpdate,
)
from business_platform.utils.enums import MembershipStatus


class MembershipController(_StubController):
    async def get_all(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[MembershipResponse]:
        db = db or self.db

        try:
            # Verify that the business exists.
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            offset = (page - 1) * size

            count_stmt = (
                select(func.count())
                .select_from(Membership)
                .where(Membership.business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(Membership)
                .where(Membership.business_id == business_id)
                .order_by(Membership.invited_at.desc().nullslast())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            memberships = result.scalars().all()

            items = [MembershipResponse.model_validate(membership) for membership in memberships]

            return PaginatedResponse[MembershipResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/memberships",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch business memberships") from exc

    async def create(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
        invited_by_id: UUID | None = None,
    ) -> MembershipResponse:
        db = db or self.db

        try:
            membership_create = MembershipCreate(**payload)

            # Verify that the business exists.
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            # Prevent the same user from being added to the same
            # business more than once.
            existing_stmt = select(Membership).where(
                Membership.business_id == business_id,
                Membership.user_id == membership_create.user_id,
            )

            existing_result = await db.execute(existing_stmt)
            existing_membership = existing_result.scalar_one_or_none()

            if existing_membership:
                raise ConflictError(
                    message=(
                        f"User {membership_create.user_id} already has "
                        f"a membership for business {business_id}"
                    )
                )

            now = datetime.now(timezone.utc)

            membership_data = membership_create.model_dump(exclude_none=True)

            membership_data["business_id"] = business_id

            if invited_by_id is not None:
                membership_data["invited_by_id"] = invited_by_id

            # Every newly created membership represents an invitation.
            membership_data["invited_at"] = now

            # If the membership is created as active, consider the user
            # to have joined immediately.
            if membership_create.status == MembershipStatus.ACTIVE:
                membership_data["joined_at"] = now

            new_membership = Membership(**membership_data)

            db.add(new_membership)

            await db.flush()
            await db.refresh(new_membership)

            return MembershipResponse.model_validate(new_membership)

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
                message=(
                    "Membership could not be created because "
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

            raise DatabaseError(message="Failed to create membership") from exc

    async def update(
        self,
        business_id: UUID,
        membership_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> MembershipResponse:
        db = db or self.db

        try:
            membership_update = MembershipUpdate(**payload)

            # Verify that the business exists.
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            # Fetch the membership scoped to the business.
            stmt = select(Membership).where(
                Membership.id == membership_id,
                Membership.business_id == business_id,
            )

            result = await db.execute(stmt)
            membership = result.scalar_one_or_none()

            if not membership:
                raise NotFoundError(
                    message=(
                        f"Membership with ID {membership_id} "
                        f"not found for business {business_id}"
                    )
                )

            update_data = membership_update.model_dump(exclude_none=True)

            if not update_data:
                return MembershipResponse.model_validate(membership)

            previous_status = membership.status

            for key, value in update_data.items():
                setattr(membership, key, value)

            now = datetime.now(timezone.utc)

            # Record the first time the membership becomes active.
            if (
                membership.status == MembershipStatus.ACTIVE
                and previous_status != MembershipStatus.ACTIVE
                and membership.joined_at is None
            ):
                membership.joined_at = now

            await db.flush()
            await db.refresh(membership)

            return MembershipResponse.model_validate(membership)

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
                message=(
                    "Membership could not be updated because "
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

            raise DatabaseError(message="Failed to update membership") from exc
