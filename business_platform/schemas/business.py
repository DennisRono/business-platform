from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from business_platform.schemas.base import BaseSchema
from business_platform.utils.enums import BusinessStatus, BusinessType, LegalStructure


class BusinessBase(BaseModel):
    """Shared fields used across Create and Update schemas."""
    name: str = Field(..., min_length=1, max_length=255, description="Legal or primary business name")
    legal_name: Optional[str] = Field(None, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    business_type: BusinessType = Field(default=BusinessType.BUSINESS)
    legal_structure: Optional[LegalStructure] = None
    status: BusinessStatus = Field(default=BusinessStatus.ACTIVE)
    registration_number: Optional[str] = Field(None, max_length=100)
    tax_identification_number: Optional[str] = Field(None, max_length=100)
    incorporation_date: Optional[date] = None
    country_of_incorporation: Optional[str] = Field(None, max_length=100)
    state_of_incorporation: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=2083)
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=30)
    country: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=150)
    industry_code: Optional[str] = Field(None, max_length=50)
    employee_count: Optional[int] = Field(None, ge=0)
    annual_revenue: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    is_public: bool = Field(default=False)
    stock_symbol: Optional[str] = Field(None, max_length=20)
    stock_exchange: Optional[str] = Field(None, max_length=50)


class BusinessCreate(BusinessBase):
    """Schema for creating a new business record. Inherits all base fields."""
    pass


class BusinessUpdate(BaseModel):
    """Schema for partially updating a business record. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    business_type: Optional[BusinessType] = None
    legal_structure: Optional[LegalStructure] = None
    status: Optional[BusinessStatus] = None
    registration_number: Optional[str] = Field(None, max_length=100)
    tax_identification_number: Optional[str] = Field(None, max_length=100)
    incorporation_date: Optional[date] = None
    country_of_incorporation: Optional[str] = Field(None, max_length=100)
    state_of_incorporation: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=2083)
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=30)
    country: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=150)
    industry_code: Optional[str] = Field(None, max_length=50)
    employee_count: Optional[int] = Field(None, ge=0)
    annual_revenue: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    is_public: Optional[bool] = None
    stock_symbol: Optional[str] = Field(None, max_length=20)
    stock_exchange: Optional[str] = Field(None, max_length=50)


class BusinessResponse(BusinessBase, BaseSchema):
    """
    Full response schema for a business record.
    Inherits audit fields (id, created_at, updated_at, etc.) from BaseSchema.
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="ignore",
    )
