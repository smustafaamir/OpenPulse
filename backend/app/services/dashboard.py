"""Dashboard service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import DashboardCreate, DashboardResponse


class DashboardService:
    """Dashboard business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._dashboards = DashboardRepository(session)

    async def create_dashboard(
        self,
        organization_id: UUID,
        data: DashboardCreate,
    ) -> DashboardResponse:
        """Create a new dashboard."""
        dashboard = await self._dashboards.create(
            organization_id=organization_id,
            name=data.name,
            layout=data.layout,
        )
        return DashboardResponse.model_validate(dashboard)

    async def list_dashboards(self, organization_id: UUID) -> list[DashboardResponse]:
        """List dashboards for an organization."""
        dashboards = await self._dashboards.list_by_org(organization_id)
        return [DashboardResponse.model_validate(d) for d in dashboards]
