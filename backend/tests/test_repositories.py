"""Repository unit tests."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event
from app.repositories.event import EventRepository
from app.repositories.organization import OrganizationRepository


async def test_event_repository_crud(db_session: AsyncSession) -> None:
    """Event repository insert, list, count, and get."""
    org_repo = OrganizationRepository(db_session)
    org = await org_repo.create("Test Org")
    await db_session.flush()

    event_repo = EventRepository(db_session)
    event = Event(
        organization_id=org.id,
        source="mock",
        event_type="price",
        symbol="BTC",
        timestamp=datetime.now(UTC),
        importance=3,
        payload={"price": 100.0},
        event_metadata={},
    )
    saved = await event_repo.insert(event)
    await db_session.flush()

    fetched = await event_repo.get_by_id(saved.id, org.id)
    assert fetched is not None
    assert fetched.symbol == "BTC"

    items = await event_repo.list_events(org.id, symbol="BTC", limit=10, offset=0)
    assert len(items) == 1

    total = await event_repo.count_events(org.id, symbol="BTC")
    assert total == 1

    missing = await event_repo.get_by_id(uuid4(), org.id)
    assert missing is None
