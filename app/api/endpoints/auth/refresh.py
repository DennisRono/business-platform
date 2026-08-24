from __future__ import annotations

from fastapi import APIRouter

from business_platform.core.exceptions import AuthenticationError
from business_platform.core.security import JWTError, create_access_token, decode_token
from business_platform.schemas.user import RefreshRequest, Token
from business_platform.utils.enums import TokenType

router = APIRouter(tags=["auth"])


@router.post("/refresh", response_model=Token, summary="Mint a new access token")
async def refresh(payload: RefreshRequest) -> Token:
    try:
        claims = decode_token(payload.refresh_token)
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired refresh token.") from exc

    if claims.get("type") != TokenType.REFRESH.value:
        raise AuthenticationError("An access token cannot be used to refresh.")

    subject = {
        "sub": claims["sub"],
        "username": claims["username"],
        "entity_id": claims.get("entity_id"),
        "role": claims["role"],
    }
    return Token(
        access_token=create_access_token(subject),
        refresh_token=payload.refresh_token,
    )