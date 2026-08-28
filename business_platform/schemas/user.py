"""
User & Auth Schemas
Pydantic v2 schemas for the Auth domain. UserCreate/UserResponse/Token
mirror the shapes already published in the OpenAPI spec field-for-field
so the contract does not shift; UserUpdate is added for the admin PATCH
flow the current spec doesn't yet expose.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from business_platform.utils.enums import Role


class UserCreate(BaseModel):
    """Payload for POST /api/v1/dashboard/register."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    full_name: Optional[str] = Field(None, max_length=255)
    role: Role = Field(default=Role.CUSTOMER)
    password: str = Field(..., min_length=8)

    model_config = ConfigDict(extra="ignore")


class UserUpdate(BaseModel):
    """Schema for partially updating a user account. All fields optional."""
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[Role] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(extra="ignore")


class UserResponse(BaseModel):
    """
    Public representation returned to clients — never includes the
    password hash. Matches the OpenAPI UserResponse component exactly.
    """
    username: str = Field(..., max_length=50, min_length=3)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    role: Role = Field(default=Role.CUSTOMER)
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")


class Token(BaseModel):
    """Access + refresh token pair returned by login / refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(extra="ignore")


class RefreshRequest(BaseModel):
    refresh_token: str
