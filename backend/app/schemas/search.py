from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SearchResult(BaseModel):
    id: UUID
    type: Literal["project", "task", "user"]
    title: str
    description: str | None = None
    url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int

    model_config = ConfigDict(from_attributes=True)
