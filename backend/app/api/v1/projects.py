from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentOrganization, RequireRole, SessionDep
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import ProjectService

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    session: SessionDep,
    current_org: CurrentOrganization,
    project_in: ProjectCreate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> ProjectResponse:
    """Create a new project in the organization."""
    return await ProjectService.create_project(session, current_org.id, project_in)  # type: ignore


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[ProjectResponse]:
    """Get all projects in the organization."""
    return await ProjectService.get_org_projects(session, current_org.id)  # type: ignore


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    session: SessionDep,
    current_org: CurrentOrganization,
    project_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> ProjectResponse:
    """Get a specific project."""
    return await ProjectService.get_project(session, current_org.id, project_id)  # type: ignore


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    session: SessionDep,
    current_org: CurrentOrganization,
    project_id: UUID,
    project_in: ProjectUpdate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> ProjectResponse:
    """Update a project."""
    return await ProjectService.update_project(session, current_org.id, project_id, project_in)  # type: ignore


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    session: SessionDep,
    current_org: CurrentOrganization,
    project_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> None:
    """Soft delete a project. Requires Admin or Owner role."""
    await ProjectService.delete_project(session, current_org.id, project_id)
