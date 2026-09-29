from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class Workflow(BaseModel):
    __tablename__ = "workflows"

    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    trigger_type: Mapped[str] = mapped_column(String(100), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    actions: Mapped[list["WorkflowAction"]] = relationship(
        "WorkflowAction",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="WorkflowAction.order",
    )


class WorkflowAction(BaseModel):
    __tablename__ = "workflow_actions"

    workflow_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("workflows.id", ondelete="CASCADE"), index=True
    )
    action_type: Mapped[str] = mapped_column(String(100))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    order: Mapped[int] = mapped_column(default=0)

    # Relationships
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="actions")
