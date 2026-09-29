from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentOrganization, RequireRole, SessionDep
from app.schemas.workflow import WorkflowCreate, WorkflowResponse
from app.services.workflow import WorkflowService

router = APIRouter()


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    session: SessionDep,
    current_org: CurrentOrganization,
    workflow_in: WorkflowCreate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> WorkflowResponse:
    """Create a new automation workflow."""
    return await WorkflowService.create_workflow(session, current_org.id, workflow_in)  # type: ignore


@router.get("", response_model=list[WorkflowResponse])
async def get_workflows(
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[WorkflowResponse]:
    """List workflows."""
    return await WorkflowService.get_workflows(session, current_org.id)  # type: ignore


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    session: SessionDep,
    current_org: CurrentOrganization,
    workflow_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> WorkflowResponse:
    """Get a workflow."""
    return await WorkflowService.get_workflow(session, current_org.id, workflow_id)  # type: ignore
