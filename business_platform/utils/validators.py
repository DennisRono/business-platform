"""Reusable validation helpers shared across schemas and controllers."""

from __future__ import annotations

import re

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")


def validate_password_strength(password: str) -> str:
    """Enforce a minimal password policy: length + at least one letter & digit.

    Returns the password unchanged when valid so it can be used directly as a
    Pydantic ``AfterValidator``. Raises ``ValueError`` otherwise, which Pydantic
    surfaces as a 422.
    """
    if len(password) < _PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {_PASSWORD_MIN_LENGTH} characters long."
        )
    if not _PASSWORD_PATTERN.match(password):
        raise ValueError("Password must contain at least one letter and one digit.")
    return password
