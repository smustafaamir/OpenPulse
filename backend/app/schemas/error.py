"""Error response schemas."""

from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Structured error payload."""

    code: str
    message: str
    details: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Top-level error wrapper."""

    error: ErrorDetail
