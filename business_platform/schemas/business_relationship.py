"""
BusinessRelationship Schemas
Pydantic v2 schemas for request/response validation of the directed
edge between two businesses.
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, model_validator

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import RelationshipStatus, RelationshipType


class BusinessRelationshipBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    related_business_id: uuid.UUID = Field(..., description="The other business in the relationship")
    relationship_type: RelationshipType = Field(...)
    status: RelationshipStatus = Field(default=RelationshipStatus.ACTIVE)
    ownership_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def check_date_order(self) -> "BusinessRelationshipBase":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class BusinessRelationshipCreate(BusinessRelationshipBase):
    """Schema for creating a new business relationship. Inherits all base fields."""
    pass


class BusinessRelationshipUpdate(BaseModel):
    """Schema for partially updating a business relationship. All fields are optional."""
    relationship_type: Optional[RelationshipType] = None
    status: Optional[RelationshipStatus] = None
    ownership_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class BusinessRelationshipResponse(BusinessRelationshipBase, BaseSchema):
    """Full response schema for a business relationship record."""
    business_id: uuid.UUID

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
