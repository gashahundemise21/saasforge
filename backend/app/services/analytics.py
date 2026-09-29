from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit_log import AuditLog
from app.models.project import Project
from app.models.task import Task
from app.schemas.analytics import DashboardStatsResponse


class AnalyticsService:
    @staticmethod
    async def get_dashboard_stats(session: AsyncSession, org_id: str | UUID) -> DashboardStatsResponse:
        # Total Projects
        projects_result = await session.execute(
            select(func.count(Project.id))
            .where(Project.organization_id == str(org_id), Project.deleted_at.is_(None))
        )
        total_projects = projects_result.scalar() or 0

        # Tasks by status
        # First get project ids for this org
        org_projects_subq = (
            select(Project.id)
            .where(Project.organization_id == str(org_id), Project.deleted_at.is_(None))
            .subquery()
        )

        status_result = await session.execute(
            select(Task.status, func.count(Task.id))
            .where(Task.project_id.in_(select(org_projects_subq)))
            .group_by(Task.status)
        )
        
        tasks_by_status: dict[str, int] = {}
        total_tasks = 0
        for row in status_result.all():
            status_val = row[0]
            count = row[1]
            tasks_by_status[status_val] = count
            total_tasks += count

        # Recent Activity (Audit Logs)
        audit_logs_result = await session.execute(
            select(AuditLog)
            .where(AuditLog.organization_id == str(org_id))
            .order_by(AuditLog.created_at.desc())
            .limit(5)
        )
        recent_activity = list(audit_logs_result.scalars().all())

        return DashboardStatsResponse(
            total_projects=total_projects,
            total_tasks=total_tasks,
            tasks_by_status=tasks_by_status,
            recent_activity=recent_activity, # type: ignore
        )
