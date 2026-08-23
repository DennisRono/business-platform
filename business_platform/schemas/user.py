"""Pydantic v2 request/response contracts for the users domain.

Follows the fixed Base / Create / Update / Response shape. ``ConfigDict
(from_attributes=True)`` (never the removed ``orm_mode``) lets Response models
be built directly from ORM instances.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

from business_platform.utils.enums import Role
from business_platform.utils.validators import validate_password_strength

Password = Annotated[str, AfterValidator(validate_password_strength)]


class UserBase(BaseModel):
    """Fields shared across create/update/response."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)
    role: Role = Role.CUSTOMER


class UserCreate(UserBase):
    """Payload for POST /users."""

    password: Password


class UserUpdate(BaseModel):
    """Payload for PATCH /users/{id}; every field optional."""

    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=255)
    role: Role | None = None
    is_active: bool | None = None
    password: Password | None = None


class UserResponse(UserBase):
    """Public representation returned to clients — never includes the hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ── Auth-flow schemas ────────────────────────────────────────────────────────
class Token(BaseModel):
    """Access + refresh token pair returned by login / refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Username + password login payload (JSON variant)."""

    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str
