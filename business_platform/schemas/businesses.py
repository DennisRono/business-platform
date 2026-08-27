from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from business_platform.utils.enums import (
    BusinessStatus,
    BusinessType,
    LegalStructure,
    OwnershipType,
)


class BusinessBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    legal_name: str | None = Field(
        default=None,
        max_length=255,
    )

    display_name: str | None = Field(
        default=None,
        max_length=255,
    )

    description: str | None = None

    business_type: BusinessType = BusinessType.BUSINESS

    legal_structure: LegalStructure | None = None

    status: BusinessStatus = BusinessStatus.ACTIVE

    registration_number: str | None = Field(
        default=None,
        max_length=100,
    )

    tax_identification_number: str | None = Field(
        default=None,
        max_length=100,
    )

    incorporation_date: date | None = None

    country_of_incorporation: str | None = Field(
        default=None,
        max_length=100,
    )

    state_of_incorporation: str | None = Field(
        default=None,
        max_length=100,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=50,
    )

    website: str | None = Field(
        default=None,
        max_length=500,
    )

    address_line_1: str | None = Field(
        default=None,
        max_length=255,
    )

    address_line_2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=30,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    industry: str | None = Field(
        default=None,
        max_length=150,
    )

    industry_code: str | None = Field(
        default=None,
        max_length=50,
    )

    employee_count: int | None = Field(
        default=None,
        ge=0,
    )

    annual_revenue: Decimal | None = Field(
        default=None,
        ge=0,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    is_public: bool = False

    stock_symbol: str | None = Field(
        default=None,
        max_length=20,
    )

    stock_exchange: str | None = Field(
        default=None,
        max_length=50,
    )


class BusinessCreate(BusinessBase):
    owner_user_id: uuid.UUID


class BusinessUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=255,
    )

    display_name: str | None = Field(
        default=None,
        max_length=255,
    )

    description: str | None = None

    business_type: BusinessType | None = None

    legal_structure: LegalStructure | None = None

    status: BusinessStatus | None = None

    registration_number: str | None = Field(
        default=None,
        max_length=100,
    )

    tax_identification_number: str | None = Field(
        default=None,
        max_length=100,
    )

    incorporation_date: date | None = None

    country_of_incorporation: str | None = None

    state_of_incorporation: str | None = None

    email: EmailStr | None = None

    phone: str | None = None

    website: str | None = None

    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None

    industry: str | None = None
    industry_code: str | None = None

    employee_count: int | None = Field(
        default=None,
        ge=0,
    )

    annual_revenue: Decimal | None = Field(
        default=None,
        ge=0,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )

    is_public: bool | None = None

    stock_symbol: str | None = None
    stock_exchange: str | None = None

    owner_user_id: uuid.UUID | None = None


class BusinessResponse(BusinessBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    owner_user_id: uuid.UUID

    created_at: datetime
    updated_at: datetime


class BusinessListResponse(BaseModel):
    items: list[BusinessResponse]

    total: int
    page: int
    size: int
    pages: int


class BusinessOwnershipCreate(BaseModel):
    owner_business_id: uuid.UUID
    owned_business_id: uuid.UUID

    ownership_type: OwnershipType = OwnershipType.MAJORITY

    ownership_percentage: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class BusinessOwnershipResponse(BusinessOwnershipCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    created_at: datetime
    updated_at: datetime
