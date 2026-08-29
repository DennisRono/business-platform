import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import (
    EmployeeHistoryEventType,
    EmploymentStatus,
    EmploymentType,
)
from business_platform.utils.types import LooseEmail


class EmployeeBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    person_id: uuid.UUID = Field(..., description="Person being employed")
    manager_id: Optional[uuid.UUID] = Field(None, description="This employee's manager")
    employee_number: Optional[str] = Field(None, max_length=50)
    job_title: Optional[str] = Field(None, max_length=150)
    department: Optional[str] = Field(None, max_length=150)
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    hire_date: Optional[date] = None
    work_email: Optional[LooseEmail] = None
    work_phone: Optional[str] = Field(None, max_length=50)


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee record. Inherits all base fields."""
    employment_status: EmploymentStatus = Field(default=EmploymentStatus.ACTIVE)

    model_config = ConfigDict(extra="forbid")


class EmployeeUpdate(BaseModel):
    """Schema for partially updating an employee record. All fields are optional."""
    manager_id: Optional[uuid.UUID] = None
    job_title: Optional[str] = Field(None, max_length=150)
    department: Optional[str] = Field(None, max_length=150)
    employment_type: Optional[EmploymentType] = None
    employment_status: Optional[EmploymentStatus] = None
    work_email: Optional[LooseEmail] = None
    work_phone: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(extra="forbid")


class EmployeeTerminateRequest(BaseModel):
    """Schema for POST .../employees/{person_id}/terminate."""
    termination_date: date = Field(...)
    termination_reason: Optional[str] = Field(None, max_length=2000)

    model_config = ConfigDict(extra="forbid")


class EmployeeResponse(EmployeeBase, BaseSchema):
    """Full response schema for an employee record."""
    business_id: uuid.UUID
    employment_status: EmploymentStatus
    termination_date: Optional[date] = None
    termination_reason: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )


class EmployeeHistoryResponse(BaseModel):
    """Represents a single logged employment lifecycle event."""
    id: uuid.UUID
    employee_id: uuid.UUID
    event_type: EmployeeHistoryEventType
    effective_date: date
    previous_job_title: Optional[str] = None
    new_job_title: Optional[str] = None
    previous_department: Optional[str] = None
    new_department: Optional[str] = None
    previous_status: Optional[EmploymentStatus] = None
    new_status: Optional[EmploymentStatus] = None
    notes: Optional[str] = None
    recorded_by_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")
