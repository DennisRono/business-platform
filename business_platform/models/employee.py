from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from business_platform.models.base import BaseModel
from business_platform.utils.enums import (
    EmployeeHistoryEventType,
    EmploymentStatus,
    EmploymentType,
)


class Employee(BaseModel):
    """Represents a Person's current employment record at a Business."""
    __tablename__ = "employees"

    business_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    person_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    manager_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True, index=True, comment="Self-referential — this employee's manager",
    )
    employee_number: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    department: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    employment_type: Mapped[EmploymentType] = mapped_column(
        String(20), default=EmploymentType.FULL_TIME, nullable=False
    )
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        String(20), default=EmploymentStatus.ACTIVE, nullable=False, index=True
    )
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    termination_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    termination_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    work_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    work_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    business: Mapped["Business"] = relationship(back_populates="employees")
    person: Mapped["Person"] = relationship(back_populates="employment_records")
    manager: Mapped["Employee | None"] = relationship(remote_side="Employee.id")
    history: Mapped[list["EmployeeHistory"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )


class EmployeeHistory(BaseModel):
    """
    Append-only log of employment lifecycle events for a single Employee.
    Read via GET .../employees/{person_id}/history.
    """
    __tablename__ = "employee_history"

    employee_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    event_type: Mapped[EmployeeHistoryEventType] = mapped_column(String(20), nullable=False, index=True)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    previous_job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    new_job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    previous_department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    new_department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    previous_status: Mapped[EmploymentStatus | None] = mapped_column(String(20), nullable=True)
    new_status: Mapped[EmploymentStatus | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    employee: Mapped["Employee"] = relationship(back_populates="history")
