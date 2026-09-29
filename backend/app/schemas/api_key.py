from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    expires_at: datetime | None = None


class ApiKeyCreate(ApiKeyBase):
    pass


class ApiKeyResponse(ApiKeyBase):
    model_config = ConfigDict(from_attributes=True)

    id: str | UUID
    organization_id: str | UUID
    prefix: str
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime


class ApiKeyCreateResponse(ApiKeyResponse):
    """Returned only once upon creation with the unhashed secret key."""
    raw_key: str
