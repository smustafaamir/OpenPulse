"""Health check endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return service health status."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(UTC),
    )
