"""Authentication dependency layer.

Exposes :data:`GetCurrentUser` — a typed FastAPI dependency that extracts and
verifies the bearer access token, then hands the handler a small, immutable
``CurrentUser`` describing the caller (``sub``, ``username``, ``entity_id``,
``role``). Token *issuance* lives in ``core/security.py``; this module is the
verification/identity side used at request time.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from business_platform.core.config import settings
from business_platform.core.exceptions import AuthenticationError
from business_platform.core.security import JWTError, decode_token
from business_platform.utils.enums import Role, TokenType

# tokenUrl is where clients POST credentials to obtain a token (login route).
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/users/login",
    auto_error=False,
)


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """Identity resolved from a verified access token."""

    sub: uuid.UUID
    username: str
    entity_id: uuid.UUID | None
    role: Role


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> CurrentUser:
    """Resolve the authenticated user from the bearer access token.

    Raises :class:`AuthenticationError` when the token is missing, malformed,
    expired, or is a refresh token being used where an access token is required.
    """
    if not token:
        raise AuthenticationError("Missing authentication credentials.")

    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token.") from exc

    if payload.get("type") != TokenType.ACCESS.value:
        raise AuthenticationError("A refresh token cannot be used to authenticate.")

    sub = payload.get("sub")
    username = payload.get("username")
    if not sub or not username:
        raise AuthenticationError("Token is missing required identity claims.")

    try:
        role = Role(payload.get("role", Role.CUSTOMER.value))
    except ValueError as exc:
        raise AuthenticationError("Token carries an unknown role.") from exc

    entity_id = payload.get("entity_id")
    return CurrentUser(
        sub=uuid.UUID(str(sub)),
        username=str(username),
        entity_id=uuid.UUID(str(entity_id)) if entity_id else None,
        role=role,
    )


# Typed alias used throughout endpoints:  user: GetCurrentUser
GetCurrentUser = Annotated[CurrentUser, Depends(get_current_user)]
