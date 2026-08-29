from __future__ import annotations

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

NOT_IMPLEMENTED_RESPONSE = {"status": "not_implemented"}

RATE_LIMIT_LIMIT_HEADER = "X-RateLimit-Limit"
RATE_LIMIT_REMAINING_HEADER = "X-RateLimit-Remaining"
RATE_LIMIT_RESET_HEADER = "X-RateLimit-Reset"
