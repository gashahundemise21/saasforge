from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class NotificationBase(BaseModel):
    title: str
    message: str
    action_url: str | None = None
    type: str

class NotificationCreate(NotificationBase):
    user_id: UUID
    organization_id: UUID

class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    organization_id: UUID
    read_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
