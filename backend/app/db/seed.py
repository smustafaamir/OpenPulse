"""Database seeding utilities."""

import asyncio
import logging
import uuid

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.models import Organization

logger = logging.getLogger(__name__)

DEFAULT_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


async def seed_default_organization() -> uuid.UUID:
    """Ensure the default organization exists for the mock collector."""
    settings = get_settings()
    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(
            select(Organization).where(Organization.id == DEFAULT_ORG_ID)
        )
        org = result.scalar_one_or_none()
        if org is None:
            org = Organization(id=DEFAULT_ORG_ID, name=settings.default_org_name)
            session.add(org)
            await session.commit()
            logger.info(
                "Seeded default organization", extra={"organization_id": str(org.id)}
            )
        return org.id


def main() -> None:
    """CLI entrypoint for seeding."""
    asyncio.run(seed_default_organization())


if __name__ == "__main__":
    main()
