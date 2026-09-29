from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentOrganization, CurrentUser, RequireRole, SessionDep
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.schemas.user import MemberResponse, UserInvite, UserResponse
from app.services.organization import OrganizationService
from app.services.audit_log import AuditLogService
from app.api.deps import CurrentActor

router = APIRouter()


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    session: SessionDep, current_user: CurrentUser, org_in: OrganizationCreate
) -> OrganizationResponse:
    """Create a new organization."""
    return await OrganizationService.create_organization(session, org_in, current_user)  # type: ignore


@router.get("/me", response_model=list[OrganizationResponse])
async def get_my_organizations(
    session: SessionDep, current_user: CurrentUser
) -> list[OrganizationResponse]:
    """Get all organizations the current user belongs to."""
    return await OrganizationService.get_user_organizations(session, current_user.id)  # type: ignore


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> OrganizationResponse:
    """Get organization details. Requires user to be in the organization."""
    return current_org  # type: ignore


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    session: SessionDep,
    current_org: CurrentOrganization,
    org_in: OrganizationUpdate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> OrganizationResponse:
    """Update organization details. Requires Owner or Admin role."""
    return await OrganizationService.update_organization(session, current_org.id, org_in)  # type: ignore


@router.get("/{org_id}/members", response_model=list[MemberResponse])
async def read_organization_members(
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[MemberResponse]:
    """Get list of members in the organization."""
    from app.services.user import UserService

    org_users = await UserService.get_organization_members(session, current_org.id)
    return [
        MemberResponse(
            user=ou.user,  # type: ignore
            role_name=ou.role.name,  # type: ignore
            joined_at=ou.created_at,
        )
        for ou in org_users
    ]


@router.post("/{org_id}/invites", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    session: SessionDep,
    current_org: CurrentOrganization,
    current_actor: CurrentActor,
    invite_in: UserInvite,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> UserResponse:
    """Invite a user to the organization. Requires Owner or Admin role."""
    from app.services.user import UserService

    return await UserService.invite_user_to_org(session, current_org, invite_in)  # type: ignore
