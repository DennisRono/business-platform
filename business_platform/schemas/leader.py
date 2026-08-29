import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import LeaderStatus, LeaderTitle


class LeaderBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    person_id: uuid.UUID = Field(..., description="Person holding the title")
    title: LeaderTitle = Field(...)
    appointed_date: Optional[date] = None
    is_signatory: bool = Field(default=False)
    voting_rights: bool = Field(default=True)
    notes: Optional[str] = None


class LeaderCreate(LeaderBase):
    """Schema for creating a new leader record. Inherits all base fields."""
    status: LeaderStatus = Field(default=LeaderStatus.ACTIVE)


class LeaderUpdate(BaseModel):
    """Schema for partially updating a leader record. All fields are optional."""
    title: Optional[LeaderTitle] = None
    status: Optional[LeaderStatus] = None
    resigned_date: Optional[date] = None
    is_signatory: Optional[bool] = None
    voting_rights: Optional[bool] = None
    notes: Optional[str] = None


class LeaderResponse(LeaderBase, BaseSchema):
    """Full response schema for a leader record."""
    business_id: uuid.UUID
    status: LeaderStatus
    resigned_date: Optional[date] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
