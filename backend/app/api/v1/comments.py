
from fastapi import APIRouter, status

from app.api.deps import CurrentActor, CurrentOrganization, SessionDep
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment import CommentService

router = APIRouter()


@router.get(
    "/tasks/{task_id}",
    response_model=list[CommentResponse],
)
async def get_task_comments(
    task_id: str,
    session: SessionDep,
    org: CurrentOrganization,
):
    """Get all comments for a specific task."""
    return await CommentService.get_comments_for_task(db=session, task_id=task_id, org_id=org.id)


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    schema: CommentCreate,
    session: SessionDep,
    org: CurrentOrganization,
    actor: CurrentActor,
):
    """Create a new comment on a task."""
    return await CommentService.create_comment(
        db=session,
        schema=schema,
        author_id=actor.actor_id,
        org_id=org.id,
    )


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    comment_id: str,
    schema: CommentUpdate,
    session: SessionDep,
    org: CurrentOrganization,
    actor: CurrentActor,
):
    """Update an existing comment."""
    return await CommentService.update_comment(
        db=session,
        comment_id=comment_id,
        schema=schema,
        user_id=actor.actor_id,
        org_id=org.id,
    )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: str,
    session: SessionDep,
    org: CurrentOrganization,
    actor: CurrentActor,
):
    """Delete a comment."""
    await CommentService.delete_comment(
        db=session,
        comment_id=comment_id,
        user_id=actor.actor_id,
        org_id=org.id,
    )
