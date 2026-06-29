"""Organization endpoints."""

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.core.deps import get_organization_service
from app.models import User
from app.schemas.organization import OrganizationResponse
from app.services.organization import OrganizationService

router = APIRouter(prefix="/organization", tags=["organization"])


@router.get("", response_model=OrganizationResponse)
async def get_organization(
    current_user: User = Depends(get_current_user),
    org_service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    """Return the current user's organization."""
    return await org_service.get_organization(current_user.organization_id)
