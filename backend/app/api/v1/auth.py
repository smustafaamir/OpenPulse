"""Authentication endpoints."""

from fastapi import APIRouter, Depends

from app.core.deps import get_auth_service
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Register a new user and organization."""
    return await auth_service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate and receive tokens."""
    return await auth_service.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Refresh an access token."""
    return await auth_service.refresh(data)
