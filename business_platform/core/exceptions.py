from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from business_platform.core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):

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


class BadRequestError(AppError):
    """The request could not be understood due to malformed syntax or invalid parameters."""

    status_code = status.HTTP_400_BAD_REQUEST
    message = "The request is malformed or contains invalid parameters."


class MethodNotAllowedError(AppError):
    """The HTTP method used is not supported for this endpoint."""

    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    message = "The HTTP method is not allowed for this endpoint."


class NotAcceptableError(AppError):
    """The server cannot produce a response matching the client's Accept headers."""

    status_code = status.HTTP_406_NOT_ACCEPTABLE
    message = "The server cannot generate a response acceptable to your client."


class RequestTimeoutError(AppError):
    """The client did not produce a request within the time the server was willing to wait."""

    status_code = status.HTTP_408_REQUEST_TIMEOUT
    message = "The request timed out. Please try again."


class GoneError(AppError):
    """The requested resource is no longer available and will not be available again."""

    status_code = status.HTTP_410_GONE
    message = "The requested resource has been permanently removed."


class PreconditionFailedError(AppError):
    """One or more preconditions given in the request headers evaluated to false."""

    status_code = status.HTTP_412_PRECONDITION_FAILED
    message = "One or more precondition checks failed."


class PayloadTooLargeError(AppError):
    """The request payload is larger than the server is willing or able to process."""

    status_code = status.HTTP_413_PAYLOAD_TOO_LARGE
    message = "The request payload is too large."


class UriTooLongError(AppError):
    """The request URI is longer than the server is willing to interpret."""

    status_code = status.HTTP_414_URI_TOO_LONG
    message = "The request URI is too long."


class UnsupportedMediaTypeError(AppError):
    """The server does not support the media type of the request payload."""

    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    message = "The media type of the request is not supported."


class UnprocessableEntityError(AppError):
    """The request was well-formed but contains semantic errors (e.g., validation failures)."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    message = "The request contains invalid or semantically erroneous data."


class IntegrityError(AppError):
    """A data integrity constraint (e.g., unique, foreign key) was violated."""

    status_code = status.HTTP_409_CONFLICT
    message = "The operation would violate data integrity constraints."


class InternalServerError(AppError):
    """A generic server-side error occurred."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "An unexpected internal server error occurred."


class ServiceUnavailableError(AppError):
    """The server is currently unable to handle the request due to temporary overload or maintenance."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    message = "The service is temporarily unavailable. Please try again later."


class GatewayTimeoutError(AppError):
    """The server, acting as a gateway, did not receive a timely response from an upstream server."""

    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    message = "The upstream server timed out."


class DatabaseError(AppError):
    """A database operation failed unexpectedly."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "A database error occurred."


class TimeoutError(AppError):
    """An operation exceeded the allowed time limit."""

    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    message = "The operation timed out."


def _error_body(error_type: str, message: str, detail: Any | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"error": {"type": error_type, "message": message}}
    if detail is not None:
        body["error"]["detail"] = detail
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that map every error type to a JSON envelope."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:

        if exc.status_code >= 500:
            logger.error("AppError: %s", exc.message, exc_info=exc)
        else:
            logger.info("AppError (%s): %s", exc.status_code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.__class__.__name__, exc.message, exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_request_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                "ValidationError",
                "Request validation failed.",
                detail=exc.errors(),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
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
