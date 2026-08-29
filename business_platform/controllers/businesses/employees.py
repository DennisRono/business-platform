from __future__ import annotations

from datetime import datetime, timezone
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
from business_platform.models.employee import Employee, EmployeeHistory
from business_platform.models.person import Person
from business_platform.schemas.base import PaginatedResponse
from business_platform.schemas.employee import (
    EmployeeCreate,
    EmployeeHistoryResponse,
    EmployeeResponse,
    EmployeeTerminateRequest,
)
from business_platform.utils.enums import EmployeeHistoryEventType, EmploymentStatus


class EmployeeController(_StubController):
    async def get_all(
        self,
        business_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[EmployeeResponse]:
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
                .select_from(Employee)
                .where(Employee.business_id == business_id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(Employee)
                .where(Employee.business_id == business_id)
                .order_by(Employee.created_at.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            employees = result.scalars().all()

            items = [EmployeeResponse.model_validate(employee) for employee in employees]

            return PaginatedResponse[EmployeeResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base or f"/businesses/{business_id}/employees",
            )

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch employees") from exc

    async def create(
        self,
        business_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> EmployeeResponse:
        db = db or self.db

        try:
            employee_create = EmployeeCreate(**payload)

            business_stmt = select(Business).where(Business.id == business_id)

            business_result = await db.execute(business_stmt)
            business = business_result.scalar_one_or_none()

            if not business:
                raise NotFoundError(message=f"Business with ID {business_id} not found")

            person_stmt = select(Person).where(Person.id == employee_create.person_id)

            person_result = await db.execute(person_stmt)
            person = person_result.scalar_one_or_none()

            if not person:
                raise NotFoundError(
                    message=f"Person with ID {employee_create.person_id} not found"
                )

            existing_stmt = select(Employee).where(
                Employee.business_id == business_id,
                Employee.person_id == employee_create.person_id,
            )

            existing_result = await db.execute(existing_stmt)
            existing_employee = existing_result.scalar_one_or_none()

            if existing_employee:
                raise ConflictError(
                    message=(
                        f"Person {employee_create.person_id} already has an "
                        f"employee record for business {business_id}"
                    )
                )

            employee_data = employee_create.model_dump(exclude_none=True)
            employee_data["business_id"] = business_id

            new_employee = Employee(**employee_data)

            db.add(new_employee)

            await db.flush()
            await db.refresh(new_employee)

            return EmployeeResponse.model_validate(new_employee)

        except (NotFoundError, BusinessLogicError, ConflictError):
            await db.rollback()
            raise

        except SQLAlchemyIntegrityError as exc:
            await db.rollback()

            raise ConflictError(
                message=(
                    "Employee could not be created because "
                    "the supplied data conflicts with an existing record"
                )
            ) from exc

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to create employee") from exc

    async def get_history(
        self,
        business_id: UUID,
        person_id: UUID,
        page: int = 1,
        size: int = 20,
        db: AsyncSession | None = None,
        url_base: str | None = None,
    ) -> PaginatedResponse[EmployeeHistoryResponse]:
        db = db or self.db

        try:
            employee_stmt = select(Employee).where(
                Employee.business_id == business_id,
                Employee.person_id == person_id,
            )

            employee_result = await db.execute(employee_stmt)
            employee = employee_result.scalar_one_or_none()

            if not employee:
                raise NotFoundError(
                    message=(
                        f"Employee record for person {person_id} "
                        f"not found for business {business_id}"
                    )
                )

            offset = (page - 1) * size

            count_stmt = (
                select(func.count())
                .select_from(EmployeeHistory)
                .where(EmployeeHistory.employee_id == employee.id)
            )

            total_result = await db.execute(count_stmt)
            total = total_result.scalar_one()

            stmt = (
                select(EmployeeHistory)
                .where(EmployeeHistory.employee_id == employee.id)
                .order_by(EmployeeHistory.effective_date.desc())
                .offset(offset)
                .limit(size)
            )

            result = await db.execute(stmt)
            history_records = result.scalars().all()

            items = [
                EmployeeHistoryResponse.model_validate(record) for record in history_records
            ]

            return PaginatedResponse[EmployeeHistoryResponse].create(
                items=items,
                total=total,
                page=page,
                size=size,
                url_base=url_base
                or f"/businesses/{business_id}/employees/{person_id}/history",
            )

        except NotFoundError:
            raise

        except SQLAlchemyError as exc:
            raise DatabaseError(message="Failed to fetch employee history") from exc

    async def terminate(
        self,
        business_id: UUID,
        person_id: UUID,
        payload: dict[str, Any],
        db: AsyncSession | None = None,
    ) -> None:
        db = db or self.db

        try:
            terminate_request = EmployeeTerminateRequest(**payload)

            employee_stmt = select(Employee).where(
                Employee.business_id == business_id,
                Employee.person_id == person_id,
            )

            employee_result = await db.execute(employee_stmt)
            employee = employee_result.scalar_one_or_none()

            if not employee:
                raise NotFoundError(
                    message=(
                        f"Employee record for person {person_id} "
                        f"not found for business {business_id}"
                    )
                )

            if employee.employment_status == EmploymentStatus.TERMINATED:
                raise BusinessLogicError(message="Employee is already terminated")

            previous_status = employee.employment_status

            employee.employment_status = EmploymentStatus.TERMINATED
            employee.termination_date = terminate_request.termination_date
            employee.termination_reason = terminate_request.termination_reason

            history_entry = EmployeeHistory(
                employee_id=employee.id,
                event_type=EmployeeHistoryEventType.TERMINATION,
                effective_date=terminate_request.termination_date,
                previous_status=previous_status,
                new_status=EmploymentStatus.TERMINATED,
                notes=terminate_request.termination_reason,
            )

            db.add(history_entry)

            await db.flush()

        except (NotFoundError, BusinessLogicError):
            await db.rollback()
            raise

        except SQLAlchemyError as exc:
            await db.rollback()

            raise DatabaseError(message="Failed to terminate employee") from exc
