from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import DataError, IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from business_platform.controllers.base import _StubController
from business_platform.core.exceptions import (
    AuthorizationError,
    BadRequestError,
    BusinessLogicError,
    ConflictError,
    DatabaseError,
    NotFoundError,
)
from business_platform.models.business import Business
from business_platform.models.business_relationship import BusinessRelationship
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.business import (
    BusinessCreate,
    BusinessResponse,
    BusinessUpdate,
)
from business_platform.schemas.business_relationship import (
    BusinessRelationshipCreate,
    BusinessRelationshipResponse,
)
from business_platform.utils.enums import BusinessStatus
from business_platform.utils.validators import BUSINESS_SORT_FIELDS, validate_sort_field


class BusinessController(_StubController):
    async def get_all(
        self,
        current_user: Any,
        page: int = 1,
        size: int = 20,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        db: AsyncSession | None = None,
        url_base: str = "/businesses",
    ) -> PaginatedResponse[BusinessResponse]:
        db = db or self.db

        try:
            if current_user.role not in {"admin", "manager"}:
                raise AuthorizationError(message="Not authorized to list businesses")

            # Validate sort field against whitelist before it touches the DB.
            sort = validate_sort_field(sort, BUSINESS_SORT_FIELDS)

            offset = (page - 1) * size

            stmt = select(Business)
            count_stmt = select(func.count()).select_from(Business)

            if q:
                search_filter = or_(
                    Business.name.ilike(f"%{q}%"),
                    Business.legal_name.ilike(f"%{q}%"),
                    Business.description.ilike(f"%{q}%"),
                )

                stmt = stmt.where(search_filter)
                count_stmt = count_stmt.where(search_filter)

            if sort:
                if sort.startswith("-"):
                    column_name = sort[1:]
                    reverse = True
                else:
                    column_name = sort
                    reverse = False

                # column_name is guaranteed safe — validate_sort_field already checked it
                order_column = getattr(Business, column_name)
                stmt = stmt.order_by(order_column.desc() if reverse else order_column)

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = stmt.offset(offset).limit(size)

            result = await db.execute(stmt)
            businesses = result.scalars().all()

            items = [BusinessResponse.model_validate(business) for business in businesses]

            return PaginatedResponse[BusinessResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base,
            )

        except (AuthorizationError, BadRequestError):
            raise
        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc
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
            business_create = BusinessCreate(**payload)

            new_business = Business(**business_create.model_dump(exclude_none=True))

            db.add(new_business)

            await db.flush()
            await db.refresh(new_business)

            return BusinessResponse.model_validate(new_business)

        except BusinessLogicError:
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Business could not be created because "
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

            raise DatabaseError(message="Failed to create business") from exc

    async def get_by_id(
        self,
        business_id: UUID,
        db: AsyncSession | None = None,
    ):
        db = db or self.db

        try:
            stmt = select(Business).where(Business.id == business_id)

            result = await db.execute(stmt)
            business = result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            return BusinessResponse.model_validate(business)

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="The request contains invalid data that could not be processed."
            ) from exc

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
            business_update = BusinessUpdate(**payload)

            stmt = select(Business).where(Business.id == business_id)

            result = await db.execute(stmt)
            business = result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            update_data = business_update.model_dump(exclude_none=True)

            for key, value in update_data.items():
                setattr(business, key, value)

            await db.flush()
            await db.refresh(business)

            return BusinessResponse.model_validate(business)

        except NotFoundError:
            await db.rollback()
            raise

        except BusinessLogicError:
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Business could not be updated because "
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

            raise DatabaseError(message="Failed to update business") from exc

    async def delete(
        self,
        business_id: UUID,
        db: AsyncSession | None = None,
    ) -> None:
        db = db or self.db

        try:
            stmt = select(Business).where(Business.id == business_id)

            result = await db.execute(stmt)
            business = result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            business.status = BusinessStatus.DISSOLVED

            await db.flush()

        except NotFoundError:
            await db.rollback()
            raise

        except BusinessLogicError:
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(message="Business could not be deleted") from exc

        except (DataError, OperationalError) as exc:
            await db.rollback()
            raise BadRequestError(
                message="The request contains invalid data that could not be processed."
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to delete business") from exc

    async def get_relationships(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str = "/businesses",
    ) -> PaginatedResponse[BusinessRelationshipResponse]:
        db = db or self.db

        try:
            business_stmt = select(Business).where(Business.id == business_id)

            result = await db.execute(business_stmt)
            business = result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            offset = (page - 1) * size

            count_stmt = (
                select(func.count())
                .select_from(BusinessRelationship)
                .where(BusinessRelationship.business_id == business_id)
            )

            stmt = (
                select(BusinessRelationship)
                .where(BusinessRelationship.business_id == business_id)
                .offset(offset)
                .limit(size)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            rel_result = await db.execute(stmt)
            relationships = rel_result.scalars().all()

            items = [BusinessRelationshipResponse.model_validate(rel) for rel in relationships]

            return PaginatedResponse[BusinessRelationshipResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=f"{url_base}/{business_id}/relationships",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

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
            rel_create = BusinessRelationshipCreate(**payload)

            stmt = select(Business).where(Business.id == business_id)

            result = await db.execute(stmt)
            source_business = result.scalar_one_or_none()

            if not source_business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            stmt = select(Business).where(Business.id == rel_create.related_business_id)

            result = await db.execute(stmt)
            related_business = result.scalar_one_or_none()

            if not related_business:
                raise NotFoundError(
                    message=(
                        "Related business with ID " f"{rel_create.related_business_id} not found"
                    )
                )

            if business_id == rel_create.related_business_id:
                raise BusinessLogicError(
                    message="A business cannot have a relationship with itself"
                )

            new_relationship = BusinessRelationship(
                business_id=business_id,
                **rel_create.model_dump(exclude_none=True),
            )

            db.add(new_relationship)

            await db.flush()
            await db.refresh(new_relationship)

            return BusinessRelationshipResponse.model_validate(new_relationship).model_dump()

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
                message="The ownership relationship conflicts with existing data"
            ) from exc

        except (DataError, OperationalError) as exc:
            await db.rollback()
            raise BadRequestError(
                message="The request contains invalid data that could not be processed."
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create business relationship") from exc
