from __future__ import annotations

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

NOT_IMPLEMENTED_RESPONSE = {"status": "not_implemented"}

RATE_LIMIT_LIMIT_HEADER = "X-RateLimit-Limit"
RATE_LIMIT_REMAINING_HEADER = "X-RateLimit-Remaining"
RATE_LIMIT_RESET_HEADER = "X-RateLimit-Reset"

AUTH_RESPONSES = {
    400: {"description": "Bad request"},
    401: {"description": "Unauthorized"},
    403: {"description": "Forbidden"},
    404: {"description": "Not found"},
    409: {"description": "Conflict"},
    422: {"description": "Validation error"},
    429: {"description": "Rate limit exceeded"},
    500: {"description": "Internal server error"},
    502: {"description": "Bad gateway"},
    503: {"description": "Service unavailable"},
}
