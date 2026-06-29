"""Background collector worker."""

import asyncio
import logging

from redis.asyncio import Redis

from app.collectors.mock import MockCollector
from app.db.seed import seed_default_organization
from app.db.session import get_session_factory
from app.events.manager import CollectorManager
from app.services.broadcast import BroadcastService

logger = logging.getLogger(__name__)


async def run_collector_loop(redis: Redis) -> None:
    """Run the mock collector pipeline until cancelled."""
    org_id = await seed_default_organization()
    session_factory = get_session_factory()
    broadcast = BroadcastService(redis)
    manager = CollectorManager(session_factory, broadcast, org_id)
    collector = MockCollector()
    logger.info("Starting mock collector for organization %s", org_id)
    await manager.process_collector(collector)


def start_collector_task(redis: Redis) -> asyncio.Task[None]:
    """Start the collector loop as a background task."""
    return asyncio.create_task(run_collector_loop(redis))
