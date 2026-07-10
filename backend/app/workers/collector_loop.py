"""Background collector worker."""

import asyncio
import logging

from redis.asyncio import Redis

from app.collectors.base import BaseCollector
from app.collectors.registry import CollectorRegistry
from app.core.config import get_settings
from app.db.seed import seed_default_organization
from app.db.session import get_session_factory
from app.events.manager import CollectorManager
from app.repositories.organization import OrganizationRepository
from app.services.broadcast import BroadcastService

logger = logging.getLogger(__name__)


async def run_single_collector(collector: BaseCollector, redis: Redis) -> None:
    """Run one collector and fan out each event to every organization."""
    session_factory = get_session_factory()
    broadcast = BroadcastService(redis)
    logger.info("Starting %s collector for all organizations", collector.source)
    async for raw_event in collector.collect():
        async with session_factory() as session:
            org_repo = OrganizationRepository(session)
            organizations = await org_repo.list_all()

        for organization in organizations:
            manager = CollectorManager(
                session_factory,
                broadcast,
                organization.id,
            )
            try:
                await manager._process_event(raw_event)
            except Exception:
                logger.exception(
                    "Failed to process %s collector event for org %s",
                    collector.source,
                    organization.id,
                )


async def run_collector_loops(redis: Redis) -> None:
    """Run all enabled collectors concurrently."""
    await seed_default_organization()
    settings = get_settings()
    registry = CollectorRegistry(settings)
    collectors = registry.get_enabled()
    logger.info("Enabled collectors: %s", ", ".join(c.source for c in collectors))
    tasks = [
        asyncio.create_task(run_single_collector(collector, redis))
        for collector in collectors
    ]
    await asyncio.gather(*tasks)


def start_collector_task(redis: Redis) -> asyncio.Task[None]:
    """Start collector loops as a background task."""
    return asyncio.create_task(run_collector_loops(redis))
