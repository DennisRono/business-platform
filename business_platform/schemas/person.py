import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.types import LooseEmail


class PersonBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    first_name: str = Field(..., min_length=1, max_length=150)
    last_name: str = Field(..., min_length=1, max_length=150)
    email: Optional[LooseEmail] = None
    phone: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[date] = None
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=30)
    country: Optional[str] = Field(None, max_length=100)


class PersonCreate(PersonBase):
    """Schema for creating a new person record. Inherits all base fields."""
    model_config = ConfigDict(extra="forbid")


class PersonUpdate(BaseModel):
    """Schema for partially updating a person record. All fields are optional."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=150)
    last_name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[LooseEmail] = None
    phone: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[date] = None
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=30)
    country: Optional[str] = Field(None, max_length=100)

    model_config = ConfigDict(extra="forbid")


class PersonResponse(PersonBase, BaseSchema):
    """Full response schema for a person record."""
    primary_business_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
