import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import OwnershipStatus, OwnershipType


class OwnershipRecordBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    person_id: uuid.UUID = Field(..., description="Person holding the stake")
    ownership_type: OwnershipType = Field(...)
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    shares_count: Optional[int] = Field(None, ge=0)
    effective_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class OwnershipRecordCreate(OwnershipRecordBase):
    """Schema for creating a new ownership record. Inherits all base fields."""
    status: OwnershipStatus = Field(default=OwnershipStatus.PENDING)

    model_config = ConfigDict(extra="forbid")


class OwnershipTransitionRequest(BaseModel):
    """
    Schema for PATCH /business/{business_id}/owners/{ownership_record_id}.
    Transitions the record to `to_status`; the prior status and an audit
    row are recorded automatically.
    """
    to_status: OwnershipStatus = Field(...)
    reason: Optional[str] = Field(None, max_length=2000)

    model_config = ConfigDict(extra="forbid")


class OwnershipRecordResponse(OwnershipRecordBase, BaseSchema):
    """Full response schema for an ownership record."""
    business_id: uuid.UUID
    status: OwnershipStatus

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )


class OwnershipTransitionResponse(BaseModel):
    """Represents a single logged status change for an OwnershipRecord."""
    id: uuid.UUID
    ownership_record_id: uuid.UUID
    from_status: Optional[OwnershipStatus] = None
    to_status: OwnershipStatus
    transitioned_at: datetime
    transitioned_by_id: Optional[uuid.UUID] = None
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")
