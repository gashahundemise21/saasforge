from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    actor_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    actor_type: Mapped[str] = mapped_column(String, nullable=False)  # "user" or "api_key"
    
    action: Mapped[str] = mapped_column(String, index=True, nullable=False)
    resource_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)

    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )

    organization: Mapped["Organization"] = relationship(back_populates="audit_logs")
