from __future__ import annotations

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

NOT_IMPLEMENTED_RESPONSE = {"status": "not_implemented"}

RATE_LIMIT_LIMIT_HEADER = "X-RateLimit-Limit"
RATE_LIMIT_REMAINING_HEADER = "X-RateLimit-Remaining"
RATE_LIMIT_RESET_HEADER = "X-RateLimit-Reset"

AUTH_RESPONSES = {
    400: {
        "description": (
            "Bad request — the request is syntactically malformed or contains "
            "invalid parameters.  Common causes: invalid sort field, query "
            "parameters that cannot be processed by the database (e.g. "
            "out-of-range integers), or a business-logic constraint violation."
        )
    },
    401: {"description": "Unauthorized — missing or invalid authentication credentials."},
    403: {"description": "Forbidden — the authenticated user lacks permission for this action."},
    404: {"description": "Not found — the requested resource does not exist."},
    409: {"description": "Conflict — the request conflicts with existing data (e.g. duplicate record)."},
    422: {
        "description": (
            "Unprocessable Entity — the request body or query parameters failed "
            "schema validation (type errors, missing required fields, extra "
            "fields on a strict schema, etc.)."
        )
    },
    429: {"description": "Too Many Requests — rate limit exceeded; slow down and retry."},
    500: {"description": "Internal Server Error — an unexpected server-side error occurred."},
    502: {"description": "Bad Gateway — an upstream dependency returned an invalid response."},
    503: {"description": "Service Unavailable — the service is temporarily unable to handle the request."},
}
