from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    task_id: str


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentResponse(CommentBase):
    id: str
    task_id: str
    author_id: str
    created_at: datetime
    updated_at: datetime

    author: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)
