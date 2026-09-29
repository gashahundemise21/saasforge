from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | UUID
    organization_id: str | UUID
    actor_id: str
    actor_type: str
    action: str
    resource_type: str
    resource_id: str | None
    details: dict[str, Any] | None
    ip_address: str | None
    created_at: datetime
