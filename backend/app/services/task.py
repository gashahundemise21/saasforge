from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import OrganizationUser
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.project import ProjectService
from app.services.workflow import WorkflowEngine


class TaskService:
    @staticmethod
    async def create_task(
        session: AsyncSession, org_id: str | UUID, project_id: str | UUID, task_in: TaskCreate
    ) -> Task:
        """Create a new task in a project."""
        # Validate project exists and belongs to org
        await ProjectService.get_project(session, org_id, project_id)

        # Validate assignee belongs to org if specified
        if task_in.assignee_id:
            result = await session.execute(
                select(OrganizationUser)
                .where(OrganizationUser.organization_id == str(org_id))
                .where(OrganizationUser.user_id == str(task_in.assignee_id))
            )
            org_user = result.scalars().first()
            if not org_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee must be a member of the organization",
                )

        task = Task(
            project_id=str(project_id),
            title=task_in.title,
            description=task_in.description,
            due_date=task_in.due_date,
            assignee_id=str(task_in.assignee_id) if task_in.assignee_id else None,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Trigger workflow
        await WorkflowEngine.trigger_event(
            session,
            org_id,
            "task.updated",
            {"task_id": task.id, "title": task.title},
        )
        return task

    @staticmethod
    async def get_project_tasks(
        session: AsyncSession, org_id: str | UUID, project_id: str | UUID
    ) -> list[Task]:
        """Get all tasks for a project."""
        # Validate project
        await ProjectService.get_project(session, org_id, project_id)

        result = await session.execute(select(Task).where(Task.project_id == str(project_id)))
        return list(result.scalars().all())

    @staticmethod
    async def get_task(session: AsyncSession, org_id: str | UUID, task_id: str | UUID) -> Task:
        """Get a specific task. Validates that the task's project belongs to the org."""
        result = await session.execute(select(Task).where(Task.id == str(task_id)))
        task = result.scalars().first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        # Validate task's project belongs to org
        await ProjectService.get_project(session, org_id, task.project_id)

        return task

    @staticmethod
    async def update_task(
        session: AsyncSession, org_id: str | UUID, task_id: str | UUID, task_in: TaskUpdate
    ) -> Task:
        """Update a task."""
        task = await TaskService.get_task(session, org_id, task_id)

        if task_in.assignee_id:
            result = await session.execute(
                select(OrganizationUser)
                .where(OrganizationUser.organization_id == str(org_id))
                .where(OrganizationUser.user_id == str(task_in.assignee_id))
            )
            org_user = result.scalars().first()
            if not org_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee must be a member of the organization",
                )

        update_data = task_in.model_dump(exclude_unset=True)
        if "assignee_id" in update_data and update_data["assignee_id"]:
            update_data["assignee_id"] = str(update_data["assignee_id"])

        for field, value in update_data.items():
            setattr(task, field, value)

        await session.commit()
        await session.refresh(task)

        # Trigger workflow
        await WorkflowEngine.trigger_event(
            session,
            org_id,
            "task.updated",
            {"task_id": task.id, "title": task.title},
        )
        return task

    @staticmethod
    async def delete_task(session: AsyncSession, org_id: str | UUID, task_id: str | UUID) -> None:
        """Delete a task (hard delete for tasks)."""
        task = await TaskService.get_task(session, org_id, task_id)
        task_id_str = str(task.id)
        task_title = task.title
        await session.delete(task)
        await session.commit()

        # Trigger workflow
        await WorkflowEngine.trigger_event(
            session,
            org_id,
            "task.deleted",
            {"task_id": task_id_str, "title": task_title},
        )
