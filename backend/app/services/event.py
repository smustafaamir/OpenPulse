"""Event service."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Event
from app.repositories.event import EventRepository
from app.schemas.event import EventCreate, EventListResponse, EventResponse
from app.services.broadcast import BroadcastService


class EventService:
    """Event ingestion and query logic."""

    def __init__(
        self,
        session: AsyncSession,
        broadcast: BroadcastService,
    ) -> None:
        self._session = session
        self._events = EventRepository(session)
        self._broadcast = broadcast

    async def create_event(
        self,
        organization_id: UUID,
        data: EventCreate,
    ) -> EventResponse:
        """Persist and broadcast a new event."""
        event = Event(
            organization_id=organization_id,
            source=data.source,
            event_type=data.event_type,
            symbol=data.symbol,
            timestamp=data.timestamp,
            importance=data.importance,
            payload=data.payload,
            event_metadata=data.metadata,
        )
        saved = await self._events.insert(event)
        response = EventResponse.from_orm_event(saved)
        await self._broadcast.publish_event(response)
        return response

    async def get_event(self, organization_id: UUID, event_id: UUID) -> EventResponse:
        """Fetch a single event."""
        event = await self._events.get_by_id(event_id, organization_id)
        if event is None:
            raise NotFoundError("Event not found")
        return EventResponse.from_orm_event(event)

    async def list_events(
        self,
        organization_id: UUID,
        *,
        symbol: str | None = None,
        source: str | None = None,
        event_type: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> EventListResponse:
        """List events with filters and pagination."""
        items = await self._events.list_events(
            organization_id,
            symbol=symbol,
            source=source,
            event_type=event_type,
            start=start,
            end=end,
            limit=limit,
            offset=offset,
        )
        total = await self._events.count_events(
            organization_id,
            symbol=symbol,
            source=source,
            event_type=event_type,
            start=start,
            end=end,
        )
        return EventListResponse(
            items=[EventResponse.from_orm_event(e) for e in items],
            total=total,
            limit=limit,
            offset=offset,
        )
