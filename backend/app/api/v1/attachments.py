from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import UUID4

from app.api.deps import CurrentActor, CurrentOrganization, RequireRole, SessionDep
from app.schemas.attachment import AttachmentResponse
from app.services.attachment import AttachmentService
from app.services.audit_log import AuditLogService

router = APIRouter()


@router.post("", response_model=AttachmentResponse)
async def upload_attachment(
    session: SessionDep,
    org: CurrentOrganization,
    actor: CurrentActor,
    file: UploadFile = File(...),
    task_id: UUID4 | None = Form(None),
    project_id: UUID4 | None = Form(None),
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> AttachmentResponse:
    if not task_id and not project_id:
        raise HTTPException(status_code=400, detail="Must provide task_id or project_id")

    attachment = await AttachmentService.create_attachment(
        session=session,
        file=file,
        organization_id=org.id,
        uploader_id=actor.actor_id,
        task_id=str(task_id) if task_id else None,
        project_id=str(project_id) if project_id else None,
    )

    await AuditLogService.log_action(
        session=session,
        org_id=org.id,
        action="attachment.uploaded",
        actor=actor,
        resource_id=attachment.id,
        resource_type="attachment",
        details={"filename": file.filename, "size": attachment.size},
    )

    return attachment


@router.get("/tasks/{task_id}", response_model=list[AttachmentResponse])
async def list_task_attachments(
    session: SessionDep,
    org: CurrentOrganization,
    task_id: UUID4,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[AttachmentResponse]:
    return await AttachmentService.list_task_attachments(session, str(task_id), org.id)


@router.get("/{attachment_id}/download")
async def download_attachment(
    session: SessionDep,
    org: CurrentOrganization,
    attachment_id: UUID4,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
):
    attachment = await AttachmentService.get_attachment(session, str(attachment_id), org.id)
    return FileResponse(
        path=attachment.file_path, filename=attachment.filename, media_type=attachment.content_type
    )


@router.delete("/{attachment_id}", status_code=204)
async def delete_attachment(
    request: Request,
    session: SessionDep,
    org: CurrentOrganization,
    actor: CurrentActor,
    attachment_id: UUID4,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
):
    attachment = await AttachmentService.get_attachment(session, str(attachment_id), org.id)

    # Only uploader or admin can delete
    org_user = getattr(request.state, "organization_user", None)
    role = org_user.role.name if org_user and org_user.role else "Member"

    if attachment.uploader_id != actor.actor_id and role not in ["Owner", "Admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this attachment")

    await AttachmentService.delete_attachment(session, str(attachment_id), org.id)

    await AuditLogService.log_action(
        session=session,
        org_id=org.id,
        action="attachment.deleted",
        actor=actor,
        resource_id=str(attachment_id),
        resource_type="attachment",
        details={"filename": attachment.filename},
    )
