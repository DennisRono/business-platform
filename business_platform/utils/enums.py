"""Shared enumerations used across domains."""

from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    """Coarse role assigned to a user, carried inside the JWT."""

    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    CUSTOMER = "customer"


class TokenType(str, Enum):
    """Distinguishes access vs. refresh tokens inside the JWT ``type`` claim."""

    ACCESS = "access"
    REFRESH = "refresh"
