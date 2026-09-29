from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class WebhookEndpoint(BaseModel):
    __tablename__ = "webhook_endpoints"

    url: Mapped[str] = mapped_column(String, nullable=False)
    secret: Mapped[str] = mapped_column(String, nullable=False)
    events: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )

    organization: Mapped["Organization"] = relationship(back_populates="webhook_endpoints")
    deliveries: Mapped[list["WebhookDelivery"]] = relationship(
        back_populates="endpoint", cascade="all, delete-orphan"
    )


class WebhookDelivery(BaseModel):
    __tablename__ = "webhook_deliveries"

    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)

    endpoint_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), index=True
    )

    endpoint: Mapped["WebhookEndpoint"] = relationship(back_populates="deliveries")
