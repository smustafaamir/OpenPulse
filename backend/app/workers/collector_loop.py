"""Background collector worker."""

import asyncio
import logging

from redis.asyncio import Redis

from app.collectors.mock import MockCollector
from app.db.seed import seed_default_organization
from app.db.session import get_session_factory
from app.events.manager import CollectorManager
from app.repositories.organization import OrganizationRepository
from app.services.broadcast import BroadcastService

logger = logging.getLogger(__name__)


async def run_collector_loop(redis: Redis) -> None:
    """Run the mock collector pipeline for every organization."""
    await seed_default_organization()
    session_factory = get_session_factory()
    broadcast = BroadcastService(redis)
    collector = MockCollector()
    logger.info("Starting mock collector for all organizations")
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
                    "Failed to process collector event for org %s",
                    organization.id,
                )


def start_collector_task(redis: Redis) -> asyncio.Task[None]:
    """Start the collector loop as a background task."""
    return asyncio.create_task(run_collector_loop(redis))
