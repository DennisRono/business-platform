import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import MembershipRole, MembershipStatus


class MembershipBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    user_id: uuid.UUID = Field(..., description="Platform user being granted access")
    role: MembershipRole = Field(default=MembershipRole.STAFF)
    status: MembershipStatus = Field(default=MembershipStatus.INVITED)


class MembershipCreate(MembershipBase):
    """Schema for inviting/creating a new membership. Inherits all base fields."""
    model_config = ConfigDict(extra="forbid")


class MembershipUpdate(BaseModel):
    """Schema for partially updating a membership. All fields are optional."""
    role: Optional[MembershipRole] = None
    status: Optional[MembershipStatus] = None
    joined_at: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")


class MembershipResponse(MembershipBase, BaseSchema):
    """Full response schema for a membership record."""
    business_id: uuid.UUID
    invited_by_id: Optional[uuid.UUID] = None
    invited_at: Optional[datetime] = None
    joined_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
