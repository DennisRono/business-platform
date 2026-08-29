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
from business_platform.models.leader import Leader
from business_platform.models.person import Person
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.leader import LeaderCreate, LeaderResponse


class LeadershipController(_StubController):
    async def get_all(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[LeaderResponse]:
        db = db or self.db

        try:
            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            offset = (page - 1) * size

            count_stmt = (
                select(func.count()).select_from(Leader).where(Leader.business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(Leader)
                .where(Leader.business_id == business_id)
                .order_by(Leader.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            leaders = result.scalars().all()

            items = [LeaderResponse.model_validate(leader) for leader in leaders]

            return PaginatedResponse[LeaderResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/leaders",
            )

        except NotFoundError:
            raise

        except (DataError, OperationalError) as exc:
            raise BadRequestError(
                message="Invalid query parameters caused a database error."
            ) from exc

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch leaders") from exc

    async def create(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> LeaderResponse:
        db = db or self.db

        try:
            leader_create = LeaderCreate(**payload)

            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            person_stmt = select(Person).where(Person.id == leader_create.person_id)

            person_result = await db.execute(person_stmt)
            person = person_result.scalar_one_or_none()

            if not person:
                raise NotFoundError(
                    message=f"Person with ID {leader_create.person_id} not found"
                )

            leader_data = leader_create.model_dump(exclude_none=True)
            leader_data["business_id"] = business_id

            new_leader = Leader(**leader_data)

            db.add(new_leader)

            await db.flush()
            await db.refresh(new_leader)

            return LeaderResponse.model_validate(new_leader)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Leader could not be created because "
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

            raise DatabaseError(message="Failed to create leader") from exc
