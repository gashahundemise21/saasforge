from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentBase(BaseModel):
    filename: str
    content_type: str
    size: int
    task_id: str | None = None
    project_id: str | None = None


class AttachmentCreate(AttachmentBase):
    file_path: str
    uploader_id: str
    organization_id: str


class AttachmentResponse(AttachmentBase):
    id: str
    created_at: datetime
    uploader_id: str

    model_config = ConfigDict(from_attributes=True)
