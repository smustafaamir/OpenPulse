"""HTTP middleware for request tracing and timing."""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppError, ErrorCode

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach request ID and log request duration."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Process a request and emit structured logs."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        org_id = getattr(request.state, "organization_id", None)
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "organization_id": org_id,
                "route": f"{request.method} {request.url.path}",
                "duration_ms": duration_ms,
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response


def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Convert AppError to the standard error response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert Pydantic validation errors to the standard format."""
    details: dict[str, str] = {}
    for error in exc.errors():
        loc = ".".join(str(part) for part in error["loc"] if part != "body")
        details[loc or "body"] = error["msg"]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "Invalid request parameters",
                "details": details,
            }
        },
    )


def internal_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "Internal server error",
                "details": {},
            }
        },
    )
