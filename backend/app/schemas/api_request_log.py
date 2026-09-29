from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Any

class ApiRequestLogResponse(BaseModel):
    id: str
    api_key_id: str
    endpoint: str
    method: str
    status_code: int
    ip_address: str | None
    user_agent: str | None
    request_payload: dict[str, Any] | None
    response_payload: dict[str, Any] | None
    duration_ms: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
