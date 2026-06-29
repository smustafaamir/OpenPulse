"""FastAPI dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.services.auth import AuthService
from app.services.broadcast import BroadcastService
from app.services.dashboard import DashboardService
from app.services.event import EventService
from app.services.organization import OrganizationService


async def get_redis(request: Request) -> AsyncGenerator[Redis]:
    """Yield the application Redis client."""
    yield request.app.state.redis


def get_auth_service(
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    """Provide AuthService."""
    return AuthService(session, settings)


def get_organization_service(
    session: AsyncSession = Depends(get_db),
) -> OrganizationService:
    """Provide OrganizationService."""
    return OrganizationService(session)


def get_event_service(
    session: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> EventService:
    """Provide EventService."""
    return EventService(session, BroadcastService(redis))


def get_dashboard_service(
    session: AsyncSession = Depends(get_db),
) -> DashboardService:
    """Provide DashboardService."""
    return DashboardService(session)
