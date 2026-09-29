from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class WebhookEndpointCreate(BaseModel):
    url: HttpUrl
    events: list[str]


class WebhookEndpointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | UUID
    organization_id: str | UUID
    url: str
    events: list[str]
    is_active: bool
    created_at: datetime


class WebhookEndpointCreateResponse(WebhookEndpointResponse):
    secret: str  # Only returned once on creation


class WebhookDeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | UUID
    endpoint_id: str | UUID
    event_type: str
    payload: dict[str, Any]
    status_code: int | None
    success: bool
    error_message: str | None
    created_at: datetime
