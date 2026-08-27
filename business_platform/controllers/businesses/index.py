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
from business_platform.models.businesses import Business, BusinessOwnership
from business_platform.schemas.businesses import (
    BusinessListResponse,
    BusinessResponse,
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
    ) -> BusinessListResponse:
        db = db or self.db

        try:
            if current_user.role not in {"admin", "manager"}:
                raise AuthorizationError(message="Not authorized to list businesses")

            query = select(Business)

            if q:
                search = f"%{q}%"

                query = query.where(
                    or_(
                        Business.name.ilike(search),
                        Business.legal_name.ilike(search),
                        Business.display_name.ilike(search),
                        Business.registration_number.ilike(search),
                        Business.industry.ilike(search),
                        Business.email.ilike(search),
                        Business.city.ilike(search),
                        Business.state.ilike(search),
                        Business.country.ilike(search),
                    )
                )

            if sort:
                descending = sort.startswith("-")
                field_name = sort[1:] if descending else sort

                allowed_fields = {
                    "name": Business.name,
                    "legal_name": Business.legal_name,
                    "created_at": Business.created_at,
                    "updated_at": Business.updated_at,
                    "industry": Business.industry,
                    "status": Business.status,
                    "business_type": Business.business_type,
                    "employee_count": Business.employee_count,
                    "annual_revenue": Business.annual_revenue,
                }

                sort_field = allowed_fields.get(
                    field_name,
                    Business.created_at,
                )

                query = query.order_by(sort_field.desc() if descending else sort_field.asc())
            else:
                query = query.order_by(Business.created_at.desc())

            count_query = select(func.count()).select_from(query.order_by(None).subquery())

            total = await db.scalar(count_query) or 0

            query = query.offset(skip).limit(limit)

            result = await db.execute(query)
            businesses = result.scalars().all()

            return BusinessListResponse(
                items=[BusinessResponse.model_validate(business) for business in businesses],
                total=total,
                page=(skip // limit) + 1 if limit > 0 else 1,
                size=limit,
                pages=((total + limit - 1) // limit if limit > 0 else 1),
            )

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch businesses") from exc

    async def create(
        self,
        payload: dict[str, Any],
        current_user: Any,
        db: AsyncSession | None = None,
    ) -> BusinessResponse:
        db = db or self.db

        try:
            if not payload:
                raise BusinessLogicError(message="Business data is required")

            allowed_fields = {
                column.name
                for column in Business.__table__.columns
                if column.name
                not in {
                    "id",
                    "created_at",
                    "updated_at",
                }
            }

            data = {key: value for key, value in payload.items() if key in allowed_fields}

            if "name" not in data or not data["name"]:
                raise BusinessLogicError(message="Business name is required")

            if data.get("website") is not None:
                data["website"] = str(data["website"])
            data["owner_user_id"] = current_user.sub

            business = Business(**data)

            db.add(business)
            await db.commit()
            await db.refresh(business)

            return BusinessResponse.model_validate(business)

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
    ) -> BusinessResponse:
        db = db or self.db

        try:
            query = select(Business).where(Business.id == business_id)

            result = await db.execute(query)
            business = result.scalar_one_or_none()

            if business is None:
                raise NotFoundError(message="Business not found")

            return BusinessResponse.model_validate(business)

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch business") from exc

    async def update(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> BusinessResponse:
        db = db or self.db

        try:
            if not payload:
                raise BusinessLogicError(message="No update data was provided")

            query = select(Business).where(Business.id == business_id)

            result = await db.execute(query)
            business = result.scalar_one_or_none()

            if business is None:
                raise NotFoundError(message="Business not found")

            protected_fields = {
                "id",
                "created_at",
                "updated_at",
                "owner_user_id",
            }

            allowed_fields = {column.name for column in Business.__table__.columns}

            for field, value in payload.items():
                if field in allowed_fields and field not in protected_fields:
                    setattr(business, field, value)

            await db.commit()
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
            query = select(Business).where(Business.id == business_id)

            result = await db.execute(query)
            business = result.scalar_one_or_none()

            if business is None:
                raise NotFoundError(message="Business not found")

            if hasattr(business, "deleted_at"):
                setattr(
                    business,
                    "deleted_at",
                    func.now(),
                )

            else:

                status_enum = type(business.status)

                inactive_status = None

                for member_name in (
                    "INACTIVE",
                    "ARCHIVED",
                    "DELETED",
                ):
                    inactive_status = status_enum.__members__.get(member_name)

                    if inactive_status is not None:
                        break

                if inactive_status is None:
                    raise BusinessLogicError(
                        message=(
                            "Business cannot be soft-deleted because "
                            "the model does not provide a deleted_at "
                            "field or an inactive status"
                        )
                    )

                business.status = inactive_status

            await db.commit()

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
            business_query = select(Business.id).where(Business.id == business_id)

            business_result = await db.execute(business_query)

            if business_result.scalar_one_or_none() is None:
                raise NotFoundError(message="Business not found")

            query = (
                select(BusinessOwnership)
                .where(
                    or_(
                        BusinessOwnership.owner_business_id == business_id,
                        BusinessOwnership.owned_business_id == business_id,
                    )
                )
                .order_by(BusinessOwnership.created_at.desc())
            )

            result = await db.execute(query)

            relationships = result.scalars().all()

            return [
                {
                    "id": relationship.id,
                    "owner_business_id": (relationship.owner_business_id),
                    "owned_business_id": (relationship.owned_business_id),
                    "ownership_type": (relationship.ownership_type.value),
                    "ownership_percentage": (relationship.ownership_percentage),
                    "created_at": (relationship.created_at),
                    "updated_at": (relationship.updated_at),
                }
                for relationship in relationships
            ]

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
            if not payload:
                raise BusinessLogicError(message="Relationship data is required")

            owner_business_id = payload.get(
                "owner_business_id",
                business_id,
            )

            owned_business_id = payload.get("owned_business_id")

            if owned_business_id is None:
                raise BusinessLogicError(message="owned_business_id is required")

            if owner_business_id == owned_business_id:
                raise BusinessLogicError(message="A business cannot own itself")

            owner_query = select(Business.id).where(Business.id == owner_business_id)

            owned_query = select(Business.id).where(Business.id == owned_business_id)

            owner_result = await db.execute(owner_query)
            owned_result = await db.execute(owned_query)

            if owner_result.scalar_one_or_none() is None:
                raise NotFoundError(message="Owner business not found")

            if owned_result.scalar_one_or_none() is None:
                raise NotFoundError(message="Owned business not found")

            existing_query = select(BusinessOwnership).where(
                BusinessOwnership.owner_business_id == owner_business_id,
                BusinessOwnership.owned_business_id == owned_business_id,
            )

            existing_result = await db.execute(existing_query)

            if existing_result.scalar_one_or_none() is not None:
                raise ConflictError(
                    message="This business ownership relationship " "already exists"
                )

            allowed_fields = {
                "owner_business_id",
                "owned_business_id",
                "ownership_type",
                "ownership_percentage",
            }

            data = {key: value for key, value in payload.items() if key in allowed_fields}

            data["owner_business_id"] = owner_business_id
            data["owned_business_id"] = owned_business_id

            relationship = BusinessOwnership(**data)

            db.add(relationship)

            await db.commit()
            await db.refresh(relationship)

            return {
                "id": relationship.id,
                "owner_business_id": (relationship.owner_business_id),
                "owned_business_id": (relationship.owned_business_id),
                "ownership_type": (relationship.ownership_type.value),
                "ownership_percentage": (relationship.ownership_percentage),
                "created_at": relationship.created_at,
                "updated_at": relationship.updated_at,
            }

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
