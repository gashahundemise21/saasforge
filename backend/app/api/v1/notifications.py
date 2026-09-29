from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4, BaseModel

from app.api.deps import CurrentActor, CurrentOrganization, RequireRole, SessionDep
from app.schemas.notification import NotificationResponse
from app.services.notification import NotificationService

router = APIRouter()


class UnreadCountResponse(BaseModel):
    unread_count: int


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    session: SessionDep,
    org: CurrentOrganization,
    actor: CurrentActor,
    skip: int = 0,
    limit: int = 50,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[NotificationResponse]:
    if actor.actor_type != "user":
        raise HTTPException(status_code=403, detail="Only users can have notifications")

    return await NotificationService.list_user_notifications(
        session, actor.actor_id, org.id, limit, skip
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    session: SessionDep,
    org: CurrentOrganization,
    actor: CurrentActor,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> UnreadCountResponse:
    if actor.actor_type != "user":
        raise HTTPException(status_code=403, detail="Only users can have notifications")

    count = await NotificationService.get_unread_count(session, actor.actor_id, org.id)
    return UnreadCountResponse(unread_count=count)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    session: SessionDep,
    org: CurrentOrganization,
    actor: CurrentActor,
    notification_id: UUID4,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> NotificationResponse:
    if actor.actor_type != "user":
        raise HTTPException(status_code=403, detail="Only users can have notifications")

    notification = await NotificationService.mark_as_read(
        session, str(notification_id), actor.actor_id, org.id
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.put("/read-all", status_code=204)
async def mark_all_notifications_as_read(
    session: SessionDep,
    org: CurrentOrganization,
    actor: CurrentActor,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
):
    if actor.actor_type != "user":
        raise HTTPException(status_code=403, detail="Only users can have notifications")

    await NotificationService.mark_all_as_read(session, actor.actor_id, org.id)
