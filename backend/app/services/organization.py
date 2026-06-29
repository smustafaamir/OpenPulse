"""Organization service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.organization import OrganizationRepository
from app.schemas.organization import OrganizationResponse


class OrganizationService:
    """Organization business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._orgs = OrganizationRepository(session)

    async def get_organization(self, organization_id: UUID) -> OrganizationResponse:
        """Return organization details."""
        org = await self._orgs.get_by_id(organization_id)
        if org is None:
            raise NotFoundError("Organization not found")
        return OrganizationResponse.model_validate(org)
