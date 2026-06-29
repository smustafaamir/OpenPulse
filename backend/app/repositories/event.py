"""Event persistence."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event


class EventRepository:
    """CRUD operations for events."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def insert(self, event: Event) -> Event:
        """Persist a new event."""
        self._session.add(event)
        await self._session.flush()
        return event

    async def get_by_id(self, event_id: UUID, organization_id: UUID) -> Event | None:
        """Fetch an event scoped to an organization."""
        result = await self._session.execute(
            select(Event).where(
                Event.id == event_id,
                Event.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

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
    ) -> list[Event]:
        """List events with optional filters."""
        query = select(Event).where(Event.organization_id == organization_id)
        if symbol is not None:
            query = query.where(Event.symbol == symbol)
        if source is not None:
            query = query.where(Event.source == source)
        if event_type is not None:
            query = query.where(Event.event_type == event_type)
        if start is not None:
            query = query.where(Event.timestamp >= start)
        if end is not None:
            query = query.where(Event.timestamp <= end)
        query = query.order_by(Event.timestamp.desc()).limit(limit).offset(offset)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def count_events(
        self,
        organization_id: UUID,
        *,
        symbol: str | None = None,
        source: str | None = None,
        event_type: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> int:
        """Count events matching filters."""
        query = (
            select(func.count())
            .select_from(Event)
            .where(Event.organization_id == organization_id)
        )
        if symbol is not None:
            query = query.where(Event.symbol == symbol)
        if source is not None:
            query = query.where(Event.source == source)
        if event_type is not None:
            query = query.where(Event.event_type == event_type)
        if start is not None:
            query = query.where(Event.timestamp >= start)
        if end is not None:
            query = query.where(Event.timestamp <= end)
        result = await self._session.execute(query)
        return int(result.scalar_one())
