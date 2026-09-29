from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class ApiRequestLog(BaseModel):
    __tablename__ = "api_request_logs"

    api_key_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("api_keys.id", ondelete="CASCADE"), index=True
    )
    endpoint: Mapped[str] = mapped_column(String, index=True)
    method: Mapped[str] = mapped_column(String)
    status_code: Mapped[int] = mapped_column(Integer)
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    request_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    response_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    api_key = relationship("ApiKey", backref="request_logs")
