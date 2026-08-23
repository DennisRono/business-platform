from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from business_platform.core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base class for all application-level errors.

    Subclasses set a default ``status_code`` and ``message``; callers may
    override the message and attach a structured ``detail`` payload.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        detail: Any | None = None,
    ) -> None:
        self.message = message or self.message
        self.detail = detail
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "The requested resource was not found."


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Authentication failed."


class AuthorizationError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    message = "You do not have permission to perform this action."


class ValidationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    message = "The submitted data is invalid."


class BusinessLogicError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "The request could not be completed due to a business rule."


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    message = "The request conflicts with the current state of the resource."


class RateLimitError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Rate limit exceeded. Please slow down."


def _error_body(error_type: str, message: str, detail: Any | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"error": {"type": error_type, "message": message}}
    if detail is not None:
        body["error"]["detail"] = detail
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that map every error type to a JSON envelope."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        # 5xx are logged as errors; expected 4xx are logged at info level.
        if exc.status_code >= 500:
            logger.error("AppError: %s", exc.message, exc_info=exc)
        else:
            logger.info("AppError (%s): %s", exc.status_code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.__class__.__name__, exc.message, exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_request_validation(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                "ValidationError",
                "Request validation failed.",
                detail=exc.errors(),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_exception(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body("HTTPException", str(exc.detail)),
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("InternalServerError", "An unexpected error occurred."),
        )
