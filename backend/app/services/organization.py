import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import SaaSForgeError
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import OrganizationUser, User
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


def _generate_slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return f"{slug}-{str(uuid.uuid4())[:8]}"


class OrganizationService:
    @staticmethod
    async def create_organization(
        session: AsyncSession, org_in: OrganizationCreate, current_user: User
    ) -> Organization:
        # Create organization
        slug = _generate_slug(org_in.name)
        organization = Organization(name=org_in.name, slug=slug)
        session.add(organization)
        await session.flush()

        # Find Owner role
        stmt = select(Role).where(Role.name == "Owner")
        result = await session.execute(stmt)
        owner_role = result.scalar_one_or_none()
        
        if not owner_role:
            raise SaaSForgeError(detail="Owner role not found in database. Run seed_roles.py", status_code=500)

        # Link user to organization as Owner
        org_user = OrganizationUser(
            organization_id=organization.id,
            user_id=current_user.id,
            role_id=owner_role.id,
        )
        session.add(org_user)
        await session.commit()
        await session.refresh(organization)
        return organization

    @staticmethod
    async def get_user_organizations(session: AsyncSession, user_id: str) -> list[Organization]:
        stmt = (
            select(Organization)
            .join(OrganizationUser)
            .where(OrganizationUser.user_id == user_id, Organization.deleted_at.is_(None))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_organization(
        session: AsyncSession, org_id: str, org_in: OrganizationUpdate
    ) -> Organization:
        stmt = select(Organization).where(Organization.id == org_id, Organization.deleted_at.is_(None))
        result = await session.execute(stmt)
        organization = result.scalar_one_or_none()
        
        if not organization:
            raise SaaSForgeError(detail="Organization not found", status_code=404)

        if org_in.name is not None:
            organization.name = org_in.name

        await session.commit()
        await session.refresh(organization)
        return organization
