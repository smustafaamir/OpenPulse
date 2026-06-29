"""Organization schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationResponse(BaseModel):
    """Organization details."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
