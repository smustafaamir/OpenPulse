"""API key persistence (stub for future use)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ApiKey


class ApiKeyRepository:
    """CRUD operations for API keys."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        organization_id: UUID,
        name: str,
        hashed_key: str,
    ) -> ApiKey:
        """Insert a new API key."""
        api_key = ApiKey(
            organization_id=organization_id,
            name=name,
            hashed_key=hashed_key,
        )
        self._session.add(api_key)
        await self._session.flush()
        return api_key

    async def get_by_hash(self, hashed_key: str) -> ApiKey | None:
        """Fetch an API key by its hash."""
        result = await self._session.execute(
            select(ApiKey).where(ApiKey.hashed_key == hashed_key)
        )
        return result.scalar_one_or_none()
