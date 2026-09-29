from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentOrganization, RequireRole, SessionDep
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task import TaskService

router = APIRouter()


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    session: SessionDep,
    current_org: CurrentOrganization,
    project_id: UUID,
    task_in: TaskCreate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> TaskResponse:
    """Create a new task in a project."""
    return await TaskService.create_task(session, current_org.id, project_id, task_in)  # type: ignore


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
    task_id: UUID,
    task_in: TaskUpdate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> TaskResponse:
    """Update a task."""
    return await TaskService.update_task(session, current_org.id, task_id, task_in)  # type: ignore


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    session: SessionDep,
    current_org: CurrentOrganization,
    task_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> None:
    """Delete a task."""
    await TaskService.delete_task(session, current_org.id, task_id)
