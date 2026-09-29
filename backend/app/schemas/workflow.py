from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkflowActionBase(BaseModel):
    action_type: str
    config: dict[str, Any]
    order: int = 0


class WorkflowActionCreate(WorkflowActionBase):
    pass


class WorkflowActionResponse(WorkflowActionBase):
    id: UUID
    workflow_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowBase(BaseModel):
    name: str
    description: str | None = None
    trigger_type: str
    is_active: bool = True


class WorkflowCreate(WorkflowBase):
    actions: list[WorkflowActionCreate]


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class WorkflowResponse(WorkflowBase):
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    actions: list[WorkflowActionResponse]

    model_config = ConfigDict(from_attributes=True)
