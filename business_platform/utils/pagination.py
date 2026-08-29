"""Reusable FastAPI dependency for pagination query parameters.

Every paginated endpoint should declare:

    params: PaginationDep

instead of repeating the Query(...) annotations inline.  This guarantees
consistent clamping, range-checks, and error messages across the whole API.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Query
from typing import Annotated

from business_platform.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


@dataclass(frozen=True, slots=True)
class PaginationParams:
    """Validated, range-checked pagination parameters."""

    page: int
    size: int


def _pagination_params(
    page: int = Query(
        1,
        ge=1,
        le=10_000,          # guard against astronomically large offsets that cause DB errors
        description="Page number (1-based)",
    ),
    size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Items per page (1–{MAX_PAGE_SIZE})",
    ),
) -> PaginationParams:
    return PaginationParams(page=page, size=size)


# Import-friendly alias — use as:  params: PaginationDep
PaginationDep = Annotated[PaginationParams, Query()]

# The actual FastAPI Depends() alias used in route signatures:
#   from business_platform.utils.pagination import PaginationQuery
#   params: PaginationQuery
from fastapi import Depends  # noqa: E402 (after dataclass definition for clarity)

PaginationQuery = Annotated[PaginationParams, Depends(_pagination_params)]
