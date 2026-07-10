"""Database bootstrap: ensure migrations are applied before seeding."""

import asyncio
import logging
import subprocess
import sys

from sqlalchemy import text

from app.db.session import get_engine

logger = logging.getLogger(__name__)

REQUIRED_TABLES = ("organizations", "users", "events", "dashboards", "api_keys")


async def _table_exists(table_name: str) -> bool:
    """Return True if a table exists in the public schema."""
    engine = get_engine()
    async with engine.connect() as connection:
        result = await connection.execute(
            text(
                "SELECT EXISTS ("
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = :table_name"
                ")"
            ),
            {"table_name": table_name},
        )
        return bool(result.scalar())


async def schema_is_ready() -> bool:
    """Return True when all required application tables exist."""
    for table_name in REQUIRED_TABLES:
        if not await _table_exists(table_name):
            return False
    return True


async def _clear_alembic_version() -> None:
    """Remove stale Alembic revision markers."""
    engine = get_engine()
    async with engine.begin() as connection:
        if await _table_exists("alembic_version"):
            await connection.execute(text("DELETE FROM alembic_version"))
            logger.warning("Cleared stale alembic_version row")


def _run_alembic_upgrade() -> None:
    """Apply database migrations via Alembic CLI."""
    logger.info("Running alembic upgrade head")
    subprocess.run(["alembic", "upgrade", "head"], check=True)


async def ensure_schema() -> None:
    """Apply migrations and repair a stamped-but-empty database if needed."""
    _run_alembic_upgrade()

    if await schema_is_ready():
        logger.info("Database schema is ready")
        return

    logger.warning(
        "Alembic is at head but required tables are missing; re-running migrations"
    )
    await _clear_alembic_version()
    _run_alembic_upgrade()

    if not await schema_is_ready():
        msg = "Database schema is still incomplete after migration repair"
        raise RuntimeError(msg)


def main() -> None:
    """CLI entrypoint for database bootstrap."""
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(ensure_schema())
    except subprocess.CalledProcessError as exc:
        logger.exception("Alembic migration failed")
        sys.exit(exc.returncode)
    except RuntimeError:
        logger.exception("Database bootstrap failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
