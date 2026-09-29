from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.api.deps import CurrentActor, CurrentOrganization, RequireRole, SessionDep
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.audit_log import AuditLogService
from app.services.project import ProjectService
from app.services.webhook import WebhookDispatcher

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    session: SessionDep,
    current_org: CurrentOrganization,
    current_actor: CurrentActor,
    project_in: ProjectCreate,
    background_tasks: BackgroundTasks,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> ProjectResponse:
    """Create a new project in the organization."""
    project = await ProjectService.create_project(session, current_org, project_in)
    
    await AuditLogService.log_action(
        session=session,
        org_id=current_org.id,
        actor=current_actor,
        action="project.created",
        resource_type="project",
        resource_id=project.id,
        details={"name": project.name}
    )
    
    await WebhookDispatcher.dispatch_event(
        session=session,
        background_tasks=background_tasks,
        org_id=current_org.id,
        event_type="project.created",
        payload={"project_id": str(project.id), "name": project.name},
    )
    await session.commit()
    
    return project  # type: ignore


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
    current_actor: CurrentActor,
    project_id: UUID,
    project_in: ProjectUpdate,
    background_tasks: BackgroundTasks,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> ProjectResponse:
    """Update a project."""
    project = await ProjectService.update_project(session, current_org.id, project_id, project_in)
    
    await AuditLogService.log_action(
        session=session,
        org_id=current_org.id,
        actor=current_actor,
        action="project.updated",
        resource_type="project",
        resource_id=project.id,
        details=project_in.model_dump(exclude_unset=True)
    )
    
    await WebhookDispatcher.dispatch_event(
        session=session,
        background_tasks=background_tasks,
        org_id=current_org.id,
        event_type="project.updated",
        payload={"project_id": str(project.id), "changes": project_in.model_dump(exclude_unset=True)},
    )
    await session.commit()
    
    return project  # type: ignore


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    session: SessionDep,
    current_org: CurrentOrganization,
    current_actor: CurrentActor,
    project_id: UUID,
    background_tasks: BackgroundTasks,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> None:
    """Soft delete a project. Requires Admin or Owner role."""
    await ProjectService.delete_project(session, current_org.id, project_id)
    
    await AuditLogService.log_action(
        session=session,
        org_id=current_org.id,
        actor=current_actor,
        action="project.deleted",
        resource_type="project",
        resource_id=project_id,
    )
    
    await WebhookDispatcher.dispatch_event(
        session=session,
        background_tasks=background_tasks,
        org_id=current_org.id,
        event_type="project.deleted",
        payload={"project_id": str(project_id)},
    )
    await session.commit()
