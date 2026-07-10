"""Dashboard endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.core.deps import get_dashboard_service
from app.models import User
from app.schemas.dashboard import DashboardCreate, DashboardResponse, DashboardUpdate
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("", response_model=list[DashboardResponse])
async def list_dashboards(
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> list[DashboardResponse]:
    """List dashboards for the organization."""
    return await dashboard_service.list_dashboards(current_user.organization_id)


@router.post("", response_model=DashboardResponse, status_code=201)
async def create_dashboard(
    data: DashboardCreate,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardResponse:
    """Create a new dashboard."""
    return await dashboard_service.create_dashboard(current_user.organization_id, data)


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: UUID,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardResponse:
    """Get a single dashboard by ID."""
    return await dashboard_service.get_dashboard(
        current_user.organization_id,
        dashboard_id,
    )


@router.patch("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: UUID,
    data: DashboardUpdate,
    current_user: User = Depends(get_current_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardResponse:
    """Update dashboard name and/or layout."""
    return await dashboard_service.update_dashboard(
        current_user.organization_id,
        dashboard_id,
        data,
    )
