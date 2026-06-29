"""Health check schema."""

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Service health status."""

    status: str
    version: str
    timestamp: datetime
