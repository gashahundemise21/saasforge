from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentActor, CurrentOrganization, RequireRole, SessionDep
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.audit_log import AuditLogService
from app.services.task import TaskService

router = APIRouter()


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    session: SessionDep,
    current_org: CurrentOrganization,
    current_actor: CurrentActor,
    project_id: UUID,
    task_in: TaskCreate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> TaskResponse:
    """Create a new task in a project."""
    task = await TaskService.create_task(session, current_org.id, project_id, task_in)
    
    await AuditLogService.log_action(
        session=session,
        org_id=current_org.id,
        actor=current_actor,
        action="task.created",
        resource_type="task",
        resource_id=task.id,
        details={"title": task.title, "project_id": str(project_id)}
    )
    await session.commit()
    
    return task  # type: ignore


@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    session: SessionDep,
    current_org: CurrentOrganization,
    project_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[TaskResponse]:
    """Get all tasks in a project."""
    return await TaskService.get_project_tasks(session, current_org.id, project_id)  # type: ignore


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    session: SessionDep,
    current_org: CurrentOrganization,
    task_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> TaskResponse:
    """Get a specific task."""
    return await TaskService.get_task(session, current_org.id, task_id)  # type: ignore


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    session: SessionDep,
    current_org: CurrentOrganization,
    current_actor: CurrentActor,
    task_id: UUID,
    task_in: TaskUpdate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> TaskResponse:
    """Update a task."""
    task = await TaskService.update_task(session, current_org.id, task_id, task_in)
    
    await AuditLogService.log_action(
        session=session,
        org_id=current_org.id,
        actor=current_actor,
        action="task.updated",
        resource_type="task",
        resource_id=task.id,
        details=task_in.model_dump(exclude_unset=True)
    )
    await session.commit()
    
    return task  # type: ignore


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    session: SessionDep,
    current_org: CurrentOrganization,
    current_actor: CurrentActor,
    task_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> None:
    """Delete a task."""
    await TaskService.delete_task(session, current_org.id, task_id)
    
    await AuditLogService.log_action(
        session=session,
        org_id=current_org.id,
        actor=current_actor,
        action="task.deleted",
        resource_type="task",
        resource_id=task_id,
    )
    await session.commit()
