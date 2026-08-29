import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import ContactType


class ContactBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    business_id: Optional[uuid.UUID] = None
    person_id: Optional[uuid.UUID] = None
    contact_type: ContactType = Field(default=ContactType.PRIMARY)
    first_name: str = Field(..., min_length=1, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    company_name: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    is_primary: bool = Field(default=False)
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    """Schema for creating a new contact. Inherits all base fields."""
    pass


class ContactUpdate(BaseModel):
    """Schema for partially updating a contact. All fields are optional."""
    contact_type: Optional[ContactType] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    company_name: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    is_primary: Optional[bool] = None
    notes: Optional[str] = None


class ContactResponse(ContactBase, BaseSchema):
    """Full response schema for a contact record."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
