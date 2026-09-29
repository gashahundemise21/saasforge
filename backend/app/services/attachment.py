import os
import shutil
import uuid
from typing import Sequence
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.attachment import Attachment
from app.models.task import Task
from app.models.project import Project

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AttachmentService:
    @staticmethod
    async def create_attachment(
        session: AsyncSession,
        file: UploadFile,
        organization_id: str,
        uploader_id: str,
        task_id: str | None = None,
        project_id: str | None = None,
    ) -> Attachment:
        if not task_id and not project_id:
            raise HTTPException(status_code=400, detail="Must provide task_id or project_id")

        if task_id:
            # Verify task belongs to organization
            task = await session.scalar(select(Task).options(joinedload(Task.project)).where(Task.id == task_id))
            if not task or task.project.organization_id != organization_id:
                raise HTTPException(status_code=404, detail="Task not found")
        
        if project_id:
            # Verify project belongs to organization
            project = await session.get(Project, project_id)
            if not project or project.organization_id != organization_id:
                raise HTTPException(status_code=404, detail="Project not found")

        # Read file
        file_ext = os.path.splitext(file.filename or "")[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        size = os.path.getsize(file_path)

        attachment = Attachment(
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            size=size,
            file_path=file_path,
            task_id=task_id,
            project_id=project_id,
            organization_id=organization_id,
            uploader_id=uploader_id,
        )

        session.add(attachment)
        await session.commit()
        await session.refresh(attachment)
        return attachment

    @staticmethod
    async def get_attachment(
        session: AsyncSession,
        attachment_id: str,
        organization_id: str,
    ) -> Attachment:
        stmt = select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.organization_id == organization_id
        )
        result = await session.execute(stmt)
        attachment = result.scalar_one_or_none()
        
        if not attachment:
            raise HTTPException(status_code=404, detail="Attachment not found")
            
        return attachment

    @staticmethod
    async def list_task_attachments(
        session: AsyncSession,
        task_id: str,
        organization_id: str,
    ) -> Sequence[Attachment]:
        task = await session.scalar(select(Task).options(joinedload(Task.project)).where(Task.id == task_id))
        if not task or task.project.organization_id != organization_id:
             raise HTTPException(status_code=404, detail="Task not found")

        stmt = select(Attachment).where(Attachment.task_id == task_id).order_by(Attachment.created_at.desc())
        result = await session.execute(stmt)
        return result.scalars().all()
        
    @staticmethod
    async def delete_attachment(
        session: AsyncSession,
        attachment_id: str,
        organization_id: str,
    ) -> None:
        attachment = await AttachmentService.get_attachment(session, attachment_id, organization_id)
        
        # Remove file from disk
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
            
        await session.delete(attachment)
        await session.commit()
