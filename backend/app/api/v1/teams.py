from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentOrganization, CurrentUser, RequireRole, SessionDep
from app.schemas.team import (
    TeamCreate,
    TeamInvitationCreate,
    TeamInvitationResponse,
    TeamMemberResponse,
    TeamResponse,
    TeamUpdate,
)
from app.services.team import TeamService

router = APIRouter()


@router.get("", response_model=list[TeamResponse])
async def get_teams(
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[TeamResponse]:
    """Get all teams in the organization."""
    return await TeamService.get_teams(session, current_org.id)  # type: ignore


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    session: SessionDep,
    current_org: CurrentOrganization,
    team_in: TeamCreate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> TeamResponse:
    """Create a new team. Requires Owner or Admin."""
    return await TeamService.create_team(session, current_org.id, team_in)  # type: ignore


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> TeamResponse:
    """Get a specific team."""
    return await TeamService.get_team(session, team_id, current_org.id)  # type: ignore


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    session: SessionDep,
    current_org: CurrentOrganization,
    team_in: TeamUpdate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> TeamResponse:
    """Update a team. Requires Owner or Admin."""
    return await TeamService.update_team(session, team_id, current_org.id, team_in)  # type: ignore


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> None:
    """Delete a team. Requires Owner or Admin."""
    await TeamService.delete_team(session, team_id, current_org.id)


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse])
async def get_team_members(
    team_id: str,
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[TeamMemberResponse]:
    """Get members of a team."""
    members = await TeamService.get_team_members(session, team_id, current_org.id)
    # The response expects a user object nested which we selectinload
    return members  # type: ignore


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: str,
    user_id: str,
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> None:
    """Remove a user from a team. Requires Owner or Admin."""
    await TeamService.remove_team_member(session, team_id, user_id, current_org.id)


@router.get("/{team_id}/invitations", response_model=list[TeamInvitationResponse])
async def get_team_invitations(
    team_id: str,
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[TeamInvitationResponse]:
    """Get pending invitations for a team."""
    return await TeamService.get_team_invitations(session, team_id, current_org.id)  # type: ignore


@router.post("/{team_id}/invitations", response_model=TeamInvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_team_invitation(
    team_id: str,
    invite_in: TeamInvitationCreate,
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> TeamInvitationResponse:
    """Invite a user to a team. Requires Owner or Admin."""
    return await TeamService.create_invitation(session, team_id, current_org.id, invite_in)  # type: ignore


@router.post("/invitations/{token}/accept", response_model=TeamMemberResponse)
async def accept_team_invitation(
    token: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> TeamMemberResponse:
    """Accept a team invitation. Organization header is not strictly required here."""
    member = await TeamService.handle_invitation(session, token, current_user, accept=True)
    # Load user explicitly for the response
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.team import TeamMember
    
    stmt = select(TeamMember).options(selectinload(TeamMember.user)).where(TeamMember.id == member.id) # type: ignore
    result = await session.execute(stmt)
    full_member = result.scalar_one()
    
    return full_member  # type: ignore


@router.post("/invitations/{token}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_team_invitation(
    token: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """Reject a team invitation."""
    await TeamService.handle_invitation(session, token, current_user, accept=False)

