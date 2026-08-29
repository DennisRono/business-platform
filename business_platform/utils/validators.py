from __future__ import annotations

import re

from business_platform.core.exceptions import BadRequestError

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")


def validate_password_strength(password: str) -> str:
    if len(password) < _PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {_PASSWORD_MIN_LENGTH} characters long."
        )
    if not _PASSWORD_PATTERN.match(password):
        raise ValueError("Password must contain at least one letter and one digit.")
    return password


# Columns on the Business model that are safe to pass to ORDER BY.
# Any value not in this set is rejected before reaching the DB.
BUSINESS_SORT_FIELDS: frozenset[str] = frozenset(
    {
        "name",
        "legal_name",
        "display_name",
        "status",
        "business_type",
        "industry",
        "employee_count",
        "annual_revenue",
        "incorporation_date",
        "created_at",
        "updated_at",
    }
)


def validate_sort_field(sort: str | None, allowed: frozenset[str]) -> str | None:
    """Validate a ``?sort=`` query parameter against an explicit allowlist.

    Accepts an optional leading ``-`` (descending prefix).  Returns the
    original value unchanged when valid, ``None`` when the input is ``None``,
    and raises :class:`BadRequestError` for unknown column names so the caller
    gets a ``400`` instead of an unhandled DB error.
    """
    if sort is None:
        return None
    column = sort.lstrip("-")
    if column not in allowed:
        raise BadRequestError(
            message=(
                f"Invalid sort field '{column}'. "
                f"Allowed values: {', '.join(sorted(allowed))}."
            )
        )
    return sort
