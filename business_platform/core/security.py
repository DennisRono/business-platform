from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from business_platform.core.config import settings
from business_platform.utils.enums import TokenType

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Passwords ────────────────────────────────────────────────────────────────
def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time verify a plaintext password against a stored hash."""
    return _pwd_context.verify(plain_password, hashed_password)


# ── JWTs ─────────────────────────────────────────────────────────────────────
def _create_token(
    subject: dict[str, Any],
    token_type: TokenType,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        **subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: dict[str, Any]) -> str:
    """Short-lived access token carrying the identity claims."""
    return _create_token(
        subject,
        TokenType.ACCESS,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: dict[str, Any]) -> str:
    """Long-lived refresh token used only to mint new access tokens."""
    return _create_token(
        subject,
        TokenType.REFRESH,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT, raising ``JWTError`` on any problem."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


__all__ = [
    "JWTError",
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]
