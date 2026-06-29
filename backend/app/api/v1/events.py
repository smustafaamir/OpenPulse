"""Event endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user
from app.core.deps import get_event_service
from app.models import User
from app.schemas.event import EventCreate, EventListResponse, EventResponse
from app.services.event import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    data: EventCreate,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Ingest a new event."""
    return await event_service.create_event(current_user.organization_id, data)


@router.get("", response_model=EventListResponse)
async def list_events(
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
    symbol: str | None = None,
    source: str | None = None,
    event_type: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> EventListResponse:
    """Query historical events with filters."""
    return await event_service.list_events(
        current_user.organization_id,
        symbol=symbol,
        source=source,
        event_type=event_type,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Get a single event by ID."""
    return await event_service.get_event(current_user.organization_id, event_id)
