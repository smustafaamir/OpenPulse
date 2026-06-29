"""Collector tests."""

import pytest
from redis.asyncio import Redis

from app.collectors.mock import MockCollector
from app.events.manager import CollectorManager
from app.repositories.event import EventRepository
from app.services.broadcast import BroadcastService


async def test_mock_collector_yields_valid_events() -> None:
    """Mock collector produces schema-valid events."""
    collector = MockCollector()
    count = 0
    async for event in collector.collect():
        assert event.source == "mock"
        assert event.symbol in {"BTC", "ETH", "SPY", "NVDA"}
        assert 1 <= event.importance <= 5
        assert event.timestamp.tzinfo is not None
        count += 1
        if count >= 1:
            break


async def test_collector_manager_persists_event(engine) -> None:
    """Collector manager persists events to the database."""
    from app.db.seed import seed_default_organization
    from app.db.session import get_session_factory

    org_id = await seed_default_organization()

    redis: Redis | None = None
    try:
        redis = Redis.from_url("redis://localhost:6379/2", decode_responses=True)
        await redis.ping()
    except (ConnectionRefusedError, OSError) as exc:
        if redis is not None:
            await redis.aclose()
        pytest.skip(f"Redis not available: {exc}")

    try:
        assert redis is not None
        manager = CollectorManager(
            get_session_factory(),
            BroadcastService(redis),
            org_id,
        )
        collector = MockCollector()
        count = 0
        async for event in collector.collect():
            await manager._process_event(event)
            count += 1
            if count >= 1:
                break

        async with get_session_factory()() as verify_session:
            event_repo = EventRepository(verify_session)
            events = await event_repo.list_events(org_id, source="mock", limit=10)
            assert len(events) >= 1
    finally:
        if redis is not None:
            await redis.aclose()
