from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import ActorContext
from app.models.audit_log import AuditLog


class AuditLogService:
    @staticmethod
    async def log_action(
        session: AsyncSession,
        org_id: str | UUID,
        actor: ActorContext,
        action: str,
        resource_type: str,
        resource_id: str | UUID | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Create an audit log asynchronously in the same transaction.
        """
        log = AuditLog(
            organization_id=str(org_id),
            actor_id=actor.actor_id,
            actor_type=actor.actor_type,
            ip_address=actor.ip_address,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=details,
        )
        session.add(log)
        # We don't commit here; we let the caller's transaction handle it.

    @staticmethod
    async def list_logs(
        session: AsyncSession, org_id: str | UUID, limit: int = 100, skip: int = 0
    ) -> list[AuditLog]:
        """Get audit logs for an organization."""
        result = await session.execute(
            select(AuditLog)
            .where(AuditLog.organization_id == str(org_id))
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
