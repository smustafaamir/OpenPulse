"""Event collector pipeline manager."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.collectors.base import BaseCollector
from app.schemas.event import EventCreate
from app.services.broadcast import BroadcastService
from app.services.event import EventService

logger = logging.getLogger(__name__)


class CollectorManager:
    """Owns the collect → validate → persist → broadcast pipeline."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        broadcast: BroadcastService,
        organization_id: UUID,
    ) -> None:
        self._session_factory = session_factory
        self._broadcast = broadcast
        self._organization_id = organization_id

    async def process_collector(self, collector: BaseCollector) -> None:
        """Run a collector and process each emitted event."""
        async for raw_event in collector.collect():
            await self._process_event(raw_event)

    async def _process_event(self, data: EventCreate) -> None:
        """Validate, persist, and broadcast a single event."""
        validated = EventCreate.model_validate(data.model_dump())
        async with self._session_factory() as session:
            event_service = EventService(session, self._broadcast)
            try:
                await event_service.create_event(self._organization_id, validated)
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed to process collector event")
                raise
