"""Application error types and HTTP mapping."""

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    """Stable API error codes."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AppError(Exception):
    """Base application error with HTTP mapping."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(AppError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid or missing token") -> None:
        super().__init__(ErrorCode.AUTHENTICATION_ERROR, message, 401)


class AuthorizationError(AppError):
    """Raised when the user lacks permission."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(ErrorCode.AUTHORIZATION_ERROR, message, 403)


class NotFoundError(AppError):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(ErrorCode.NOT_FOUND, message, 404)


class ConflictError(AppError):
    """Raised when a resource already exists."""

    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(ErrorCode.CONFLICT, message, 409)
