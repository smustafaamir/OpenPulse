"""Organization persistence."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization


class OrganizationRepository:
    """CRUD operations for organizations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, name: str, org_id: UUID | None = None) -> Organization:
        """Insert a new organization."""
        org = Organization(name=name)
        if org_id is not None:
            org.id = org_id
        self._session.add(org)
        await self._session.flush()
        return org

    async def get_by_id(self, org_id: UUID) -> Organization | None:
        """Fetch an organization by ID."""
        result = await self._session.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()
