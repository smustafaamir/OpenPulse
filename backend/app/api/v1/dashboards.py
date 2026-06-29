"""Dashboard endpoints."""

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.core.deps import get_dashboard_service
from app.models import User
from app.schemas.dashboard import DashboardCreate, DashboardResponse
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
