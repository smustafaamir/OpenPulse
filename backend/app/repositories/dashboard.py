"""Dashboard persistence."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Dashboard


class DashboardRepository:
    """CRUD operations for dashboards."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        organization_id: UUID,
        name: str,
        layout: dict[str, Any],
    ) -> Dashboard:
        """Insert a new dashboard."""
        dashboard = Dashboard(
            organization_id=organization_id,
            name=name,
            layout=layout,
        )
        self._session.add(dashboard)
        await self._session.flush()
        return dashboard

    async def list_by_org(self, organization_id: UUID) -> list[Dashboard]:
        """List dashboards for an organization."""
        result = await self._session.execute(
            select(Dashboard)
            .where(Dashboard.organization_id == organization_id)
            .order_by(Dashboard.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(
        self, dashboard_id: UUID, organization_id: UUID
    ) -> Dashboard | None:
        """Fetch a dashboard scoped to an organization."""
        result = await self._session.execute(
            select(Dashboard).where(
                Dashboard.id == dashboard_id,
                Dashboard.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        dashboard_id: UUID,
        organization_id: UUID,
        *,
        name: str | None = None,
        layout: dict[str, Any] | None = None,
    ) -> Dashboard | None:
        """Update a dashboard scoped to an organization."""
        dashboard = await self.get_by_id(dashboard_id, organization_id)
        if dashboard is None:
            return None
        if name is not None:
            dashboard.name = name
        if layout is not None:
            dashboard.layout = layout
        await self._session.flush()
        return dashboard
