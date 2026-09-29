from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import SaaSForgeError
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import OrganizationUser, User
from app.schemas.user import UserCreate, UserInvite, UserUpdate
from app.services.quota import QuotaService


class UserService:
    @staticmethod
    async def get_by_email(session: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
        existing = await UserService.get_by_email(session, user_in.email)
        if existing:
            raise SaaSForgeError(detail="User with this email already exists", status_code=400)

        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def update_user(session: AsyncSession, user: User, user_in: UserUpdate) -> User:
        if user_in.email is not None and user_in.email != user.email:
            existing = await UserService.get_by_email(session, user_in.email)
            if existing:
                raise SaaSForgeError(detail="Email already in use", status_code=400)
            user.email = user_in.email

        if user_in.password is not None:
            user.hashed_password = get_password_hash(user_in.password)

        if user_in.is_active is not None:
            user.is_active = user_in.is_active

        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def invite_user_to_org(
        session: AsyncSession, organization: Organization, invite_in: UserInvite
    ) -> User:
        await QuotaService.check_member_quota(session, organization)

        # Check if role exists
        stmt = select(Role).where(Role.name == invite_in.role_name)
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            raise SaaSForgeError(detail=f"Role {invite_in.role_name} not found", status_code=400)

        # Get or create user
        user = await UserService.get_by_email(session, invite_in.email)
        if not user:
            # Create a user with a random unusable password (requires reset)
            user = User(
                email=invite_in.email,
                hashed_password="!",  # invalid hash, meaning they must reset
                is_active=True,
            )
            session.add(user)
            await session.flush()

        # Check if user is already in organization
        stmt = select(OrganizationUser).where(
            OrganizationUser.user_id == user.id,
            OrganizationUser.organization_id == organization.id,
        )
        result = await session.execute(stmt)
        org_user = result.scalar_one_or_none()
        if org_user:
            raise SaaSForgeError(
                detail="User is already a member of this organization", status_code=400
            )

        # Add user to organization
        new_org_user = OrganizationUser(
            organization_id=organization.id,
            user_id=user.id,
            role_id=role.id,
        )
        session.add(new_org_user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_organization_members(
        session: AsyncSession, org_id: str
    ) -> list[OrganizationUser]:
        stmt = (
            select(OrganizationUser)
            .options(selectinload(OrganizationUser.user), selectinload(OrganizationUser.role))
            .where(OrganizationUser.organization_id == org_id)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
