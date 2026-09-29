from datetime import UTC, datetime

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import SaaSForgeError
from app.models.comment import Comment
from app.models.project import Project
from app.models.task import Task
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    @staticmethod
    async def _get_task_and_verify_access(db: AsyncSession, task_id: str, org_id: str) -> Task:
        stmt = (
            select(Task)
            .join(Project, Task.project_id == Project.id)
            .where(
                Task.id == task_id, Project.organization_id == org_id, Project.deleted_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            raise SaaSForgeError(
                message="Task not found or access denied",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return task

    @staticmethod
    async def get_comments_for_task(db: AsyncSession, task_id: str, org_id: str) -> list[Comment]:
        # Verify access
        await CommentService._get_task_and_verify_access(db, task_id, org_id)

        stmt = (
            select(Comment)
            .where(Comment.task_id == task_id, Comment.deleted_at.is_(None))
            .options(selectinload(Comment.author))
            .order_by(Comment.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_comment(
        db: AsyncSession,
        schema: CommentCreate,
        author_id: str,
        org_id: str,
    ) -> Comment:
        # Verify access
        await CommentService._get_task_and_verify_access(db, schema.task_id, org_id)

        comment = Comment(
            task_id=schema.task_id,
            author_id=author_id,
            content=schema.content,
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)

        # Load author for response
        stmt = select(Comment).where(Comment.id == comment.id).options(selectinload(Comment.author))
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def update_comment(
        db: AsyncSession,
        comment_id: str,
        schema: CommentUpdate,
        user_id: str,
        org_id: str,
    ) -> Comment:
        stmt = (
            select(Comment)
            .join(Task, Comment.task_id == Task.id)
            .join(Project, Task.project_id == Project.id)
            .where(
                Comment.id == comment_id,
                Project.organization_id == org_id,
                Comment.deleted_at.is_(None),
            )
            .options(selectinload(Comment.author))
        )
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            raise SaaSForgeError(
                message="Comment not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Only author can update
        if str(comment.author_id) != user_id:
            raise SaaSForgeError(
                message="Cannot edit another user's comment",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        comment.content = schema.content
        comment.updated_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(comment)
        return comment

    @staticmethod
    async def delete_comment(
        db: AsyncSession,
        comment_id: str,
        user_id: str,
        org_id: str,
    ) -> None:
        stmt = (
            select(Comment)
            .join(Task, Comment.task_id == Task.id)
            .join(Project, Task.project_id == Project.id)
            .where(
                Comment.id == comment_id,
                Project.organization_id == org_id,
                Comment.deleted_at.is_(None),
            )
        )
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            raise SaaSForgeError(
                message="Comment not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Allow author to delete, could also allow org admins later
        if str(comment.author_id) != user_id:
            raise SaaSForgeError(
                message="Cannot delete another user's comment",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        comment.deleted_at = datetime.now(UTC)
        await db.commit()
