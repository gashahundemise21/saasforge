from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import QuotaExceededError
from app.core.quotas import get_quota
from app.models.organization import Organization
from app.models.project import Project
from app.models.user import OrganizationUser


class QuotaService:
    @staticmethod
    async def check_project_quota(session: AsyncSession, org: Organization) -> None:
        """Check if the organization can create another project."""
        limit = get_quota(org.plan_id, "max_projects")
        if limit == -1:
            return  # Unlimited

        result = await session.execute(
            select(func.count(Project.id)).where(Project.organization_id == org.id)
        )
        current_count = result.scalar() or 0

        if current_count >= limit:
            raise QuotaExceededError(
                message=f"Project quota exceeded. Your plan allows {limit} projects.",
                code="PROJECT_QUOTA_EXCEEDED"
            )

    @staticmethod
    async def check_member_quota(session: AsyncSession, org: Organization) -> None:
        """Check if the organization can invite another member."""
        limit = get_quota(org.plan_id, "max_members")
        if limit == -1:
            return  # Unlimited

        result = await session.execute(
            select(func.count(OrganizationUser.id)).where(OrganizationUser.organization_id == org.id)
        )
        current_count = result.scalar() or 0

        if current_count >= limit:
            raise QuotaExceededError(
                message=f"Member quota exceeded. Your plan allows {limit} members.",
                code="MEMBER_QUOTA_EXCEEDED"
            )
