import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import CompensationFrequency, CompensationType


class CompensationRecordBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    person_id: uuid.UUID = Field(..., description="Person being compensated")
    compensation_type: CompensationType = Field(...)
    frequency: CompensationFrequency = Field(...)
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    effective_date: date = Field(...)
    end_date: Optional[date] = None
    notes: Optional[str] = None


class CompensationRecordCreate(CompensationRecordBase):
    """Schema for creating a new compensation record. Inherits all base fields."""
    pass


class CompensationRecordUpdate(BaseModel):
    """Schema for partially updating a compensation record. All fields are optional."""
    amount: Optional[Decimal] = Field(None, gt=0)
    frequency: Optional[CompensationFrequency] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    notes: Optional[str] = None


class CompensationRecordResponse(CompensationRecordBase, BaseSchema):
    """Full response schema for a compensation record."""
    business_id: uuid.UUID
    is_current: bool

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
