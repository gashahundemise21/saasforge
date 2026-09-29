import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import SaaSForgeError
from app.models.team import Team, TeamMember, TeamInvitation
from app.models.organization import Organization
from app.models.user import User, OrganizationUser
from app.schemas.team import TeamCreate, TeamUpdate, TeamInvitationCreate


class TeamService:
    @staticmethod
    async def get_teams(session: AsyncSession, organization_id: str) -> list[Team]:
        stmt = select(Team).where(Team.organization_id == organization_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_team(session: AsyncSession, team_id: str, organization_id: str) -> Team:
        stmt = select(Team).where(Team.id == team_id, Team.organization_id == organization_id)
        result = await session.execute(stmt)
        team = result.scalar_one_or_none()
        if not team:
            raise SaaSForgeError(message="Team not found", status_code=404)
        return team

    @staticmethod
    async def create_team(session: AsyncSession, organization_id: str, team_in: TeamCreate) -> Team:
        team = Team(
            organization_id=organization_id,
            name=team_in.name,
            description=team_in.description,
        )
        session.add(team)
        await session.commit()
        await session.refresh(team)
        return team

    @staticmethod
    async def update_team(
        session: AsyncSession, team_id: str, organization_id: str, team_in: TeamUpdate
    ) -> Team:
        team = await TeamService.get_team(session, team_id, organization_id)
        
        if team_in.name is not None:
            team.name = team_in.name
        if team_in.description is not None:
            team.description = team_in.description
            
        await session.commit()
        await session.refresh(team)
        return team

    @staticmethod
    async def delete_team(session: AsyncSession, team_id: str, organization_id: str) -> None:
        team = await TeamService.get_team(session, team_id, organization_id)
        await session.delete(team)
        await session.commit()

    @staticmethod
    async def get_team_members(session: AsyncSession, team_id: str, organization_id: str) -> list[TeamMember]:
        # Validate team exists
        await TeamService.get_team(session, team_id, organization_id)
        
        stmt = select(TeamMember).options(selectinload(TeamMember.user)).where(TeamMember.team_id == team_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def remove_team_member(session: AsyncSession, team_id: str, user_id: str, organization_id: str) -> None:
        # Validate team exists
        await TeamService.get_team(session, team_id, organization_id)
        
        stmt = select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        result = await session.execute(stmt)
        member = result.scalar_one_or_none()
        
        if not member:
            raise SaaSForgeError(message="User is not a member of this team", status_code=404)
            
        await session.delete(member)
        await session.commit()

    @staticmethod
    async def create_invitation(
        session: AsyncSession, team_id: str, organization_id: str, invite_in: TeamInvitationCreate
    ) -> TeamInvitation:
        # Validate team exists
        await TeamService.get_team(session, team_id, organization_id)
        
        # Check if user is in org
        stmt = select(User).join(OrganizationUser).where(
            User.email == invite_in.email,
            OrganizationUser.organization_id == organization_id
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise SaaSForgeError(message="User must be in the organization before joining a team", status_code=400)
            
        # Check if already a member
        stmt = select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user.id)
        result = await session.execute(stmt)
        existing_member = result.scalar_one_or_none()
        
        if existing_member:
            raise SaaSForgeError(message="User is already a member of this team", status_code=400)
            
        # Generate invitation
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        invitation = TeamInvitation(
            team_id=team_id,
            email=invite_in.email,
            role=invite_in.role,
            token=token,
            expires_at=expires_at,
            status="pending"
        )
        
        session.add(invitation)
        await session.commit()
        await session.refresh(invitation)
        return invitation

    @staticmethod
    async def get_team_invitations(session: AsyncSession, team_id: str, organization_id: str) -> list[TeamInvitation]:
        await TeamService.get_team(session, team_id, organization_id)
        stmt = select(TeamInvitation).where(TeamInvitation.team_id == team_id, TeamInvitation.status == "pending")
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def handle_invitation(
        session: AsyncSession, token: str, current_user: User, accept: bool
    ) -> TeamMember | None:
        stmt = select(TeamInvitation).options(selectinload(TeamInvitation.team)).where(TeamInvitation.token == token)
        result = await session.execute(stmt)
        invitation = result.scalar_one_or_none()
        
        if not invitation:
            raise SaaSForgeError(message="Invalid or expired invitation token", status_code=404)
            
        if invitation.status != "pending":
            raise SaaSForgeError(message="Invitation has already been processed", status_code=400)
            
        if invitation.email != current_user.email:
            raise SaaSForgeError(message="This invitation was sent to a different email address", status_code=403)
            
        if invitation.expires_at < datetime.now(timezone.utc):
            invitation.status = "expired"
            await session.commit()
            raise SaaSForgeError(message="Invitation has expired", status_code=400)
            
        if not accept:
            invitation.status = "rejected"
            await session.commit()
            return None
            
        # Verify user is in the org of the team
        stmt = select(OrganizationUser).where(
            OrganizationUser.user_id == current_user.id,
            OrganizationUser.organization_id == invitation.team.organization_id
        )
        result = await session.execute(stmt)
        org_user = result.scalar_one_or_none()
        
        if not org_user:
            raise SaaSForgeError(message="You must be a member of the organization to join this team", status_code=403)
            
        invitation.status = "accepted"
        
        team_member = TeamMember(
            team_id=invitation.team_id,
            user_id=current_user.id,
            role=invitation.role
        )
        
        session.add(team_member)
        await session.commit()
        await session.refresh(team_member)
        
        return team_member
