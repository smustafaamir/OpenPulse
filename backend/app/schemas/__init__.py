"""Pydantic request and response schemas."""

from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.dashboard import DashboardCreate, DashboardResponse
from app.schemas.error import ErrorDetail, ErrorResponse
from app.schemas.event import EventCreate, EventListResponse, EventResponse
from app.schemas.health import HealthResponse
from app.schemas.organization import OrganizationResponse

__all__ = [
    "DashboardCreate",
    "DashboardResponse",
    "ErrorDetail",
    "ErrorResponse",
    "EventCreate",
    "EventListResponse",
    "EventResponse",
    "HealthResponse",
    "LoginRequest",
    "OrganizationResponse",
    "RefreshRequest",
    "RegisterRequest",
    "TokenResponse",
]
