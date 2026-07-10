"""Dashboard schemas."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DashboardCreate(BaseModel):
    """Dashboard creation payload."""

    name: str = Field(min_length=1, max_length=255)
    layout: dict[str, Any] = Field(default_factory=dict)


class DashboardUpdate(BaseModel):
    """Dashboard update payload."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    layout: dict[str, Any] | None = None


class DashboardResponse(BaseModel):
    """Dashboard details."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    layout: dict[str, Any]
