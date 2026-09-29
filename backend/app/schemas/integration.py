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


class IntegrationConnectionResponse(BaseModel):
    id: str
    organization_id: str
    provider: str
    is_active: bool
    settings: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
