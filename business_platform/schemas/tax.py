"""
TaxProfile / TaxIdentifier Schemas
Pydantic v2 schemas for request/response validation of tax profiles
and the sensitive identifiers attached to them.

TaxIdentifierResponse deliberately exposes only `identifier_last4`,
never the encrypted value — decrypting for display is out of scope
for a list/read schema and should go through a dedicated,
permission-gated reveal endpoint if ever needed.
"""
import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import TaxIdentifierType, TaxProfileStatus


class TaxProfileBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    jurisdiction: str = Field(..., min_length=1, max_length=100)
    filing_frequency: Optional[str] = Field(None, max_length=30)
    fiscal_year_end: Optional[str] = Field(None, max_length=5, description="MM-DD")
    notes: Optional[str] = None


class TaxProfileCreate(TaxProfileBase):
    """Schema for creating a new tax profile. Inherits all base fields."""
    status: TaxProfileStatus = Field(default=TaxProfileStatus.ACTIVE)


class TaxProfileUpdate(BaseModel):
    """Schema for partially updating a tax profile. All fields are optional."""
    filing_frequency: Optional[str] = Field(None, max_length=30)
    fiscal_year_end: Optional[str] = Field(None, max_length=5)
    status: Optional[TaxProfileStatus] = None
    notes: Optional[str] = None


class TaxProfileResponse(TaxProfileBase, BaseSchema):
    """Full response schema for a tax profile record."""
    business_id: uuid.UUID
    status: TaxProfileStatus

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )


class TaxIdentifierCreate(BaseModel):
    """
    Schema for registering a new tax identifier. `identifier_value` is
    accepted here in plaintext over TLS and must be encrypted by the
    controller/service layer before persisting — it is never echoed
    back in any response schema.
    """
    identifier_type: TaxIdentifierType = Field(...)
    identifier_value: str = Field(..., min_length=1, max_length=64)
    issued_country: Optional[str] = Field(None, max_length=100)
    issued_date: Optional[date] = None
    expiry_date: Optional[date] = None


class TaxIdentifierResponse(BaseModel):
    """Masked response schema for a tax identifier — never the raw value."""
    id: uuid.UUID
    tax_profile_id: uuid.UUID
    identifier_type: TaxIdentifierType
    identifier_last4: Optional[str] = None
    issued_country: Optional[str] = None
    issued_date: Optional[date] = None
    expiry_date: Optional[date] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="ignore")
