from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    assignee_id: str | UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = None  # todo, in_progress, done
    due_date: datetime | None = None
    assignee_id: str | UUID | None = None


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: str | UUID
    project_id: str | UUID
    status: str
    assignee_id: str | UUID | None
    created_at: datetime
    updated_at: datetime
