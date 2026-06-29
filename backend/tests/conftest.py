"""Pytest configuration and shared fixtures."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://openpulse:openpulse@localhost:5432/openpulse",
)
os.environ["REDIS_URL"] = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
os.environ["JWT_SECRET"] = "test-secret-key-for-openpulse-tests"

from app.core.config import get_settings  # noqa: E402
from app.core.deps import get_redis  # noqa: E402

get_settings.cache_clear()

from app.db.session import Base, get_session_factory, reset_db_globals  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine]:
    """Create and tear down database schema for the test session."""
    reset_db_globals()
    test_engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    except (ConnectionRefusedError, OSError) as exc:
        await test_engine.dispose()
        pytest.skip(f"PostgreSQL not available: {exc}")
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    reset_db_globals()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """Provide a database session per test."""
    reset_db_globals()
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(engine: AsyncEngine) -> AsyncGenerator[AsyncClient]:
    """HTTP test client without background collector."""
    reset_db_globals()

    redis: Redis | None = None
    try:
        redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
        await redis.ping()
    except (ConnectionRefusedError, OSError) as exc:
        if redis is not None:
            await redis.aclose()
        pytest.skip(f"Redis not available: {exc}")

    assert redis is not None
    app = create_app()

    @asynccontextmanager
    async def test_lifespan(_app):  # type: ignore[no-untyped-def]
        from app.websocket.handler import create_events_ws_router
        from app.websocket.manager import ConnectionManager

        _app.state.redis = redis
        _app.include_router(create_events_ws_router(ConnectionManager(redis)))
        yield

    app.router.lifespan_context = test_lifespan  # type: ignore[method-assign]

    async def override_get_redis() -> AsyncGenerator[Redis]:
        yield redis

    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=transport, base_url="http://test") as ac,
    ):
        yield ac

    app.dependency_overrides.clear()
    await redis.aclose()
