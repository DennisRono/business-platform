"""Project-wide constant values.

Keep magic numbers and repeated string literals here so they have exactly one
definition and are easy to audit.
"""

from __future__ import annotations

# Pagination defaults for list (GET /) endpoints.
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Standard placeholder body returned by not-yet-implemented stub handlers.
NOT_IMPLEMENTED_RESPONSE = {"status": "not_implemented"}

# Rate-limit response header names.
RATE_LIMIT_LIMIT_HEADER = "X-RateLimit-Limit"
RATE_LIMIT_REMAINING_HEADER = "X-RateLimit-Remaining"
RATE_LIMIT_RESET_HEADER = "X-RateLimit-Reset"
