"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration payload."""

    email: EmailStr
    password: str = Field(min_length=8)
    organization_name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    """User login payload."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Token refresh payload."""

    refresh_token: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
