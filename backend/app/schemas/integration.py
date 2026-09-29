from typing import Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class IntegrationConnectionBase(BaseModel):
    provider: str
    is_active: bool = True
    credentials: dict[str, Any] = {}
    settings: dict[str, Any] = {}


class IntegrationConnectionCreate(IntegrationConnectionBase):
    pass


class IntegrationConnectionUpdate(BaseModel):
    is_active: bool | None = None
    credentials: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None


class IntegrationConnectionResponse(IntegrationConnectionBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
