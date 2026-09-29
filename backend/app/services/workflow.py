from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import SaaSForgeError
from app.models.workflow import Workflow, WorkflowAction
from app.schemas.workflow import WorkflowCreate
from app.worker import async_task, celery_app


class WorkflowService:
    @staticmethod
    async def create_workflow(
        session: AsyncSession, org_id: str | UUID, workflow_in: WorkflowCreate
    ) -> Workflow:
        workflow = Workflow(
            organization_id=str(org_id),
            name=workflow_in.name,
            description=workflow_in.description,
            trigger_type=workflow_in.trigger_type,
            is_active=workflow_in.is_active,
        )
        session.add(workflow)
        await session.flush()

        for action_in in workflow_in.actions:
            action = WorkflowAction(
                workflow_id=workflow.id,
                action_type=action_in.action_type,
                config=action_in.config,
                order=action_in.order,
            )
            session.add(action)

        await session.commit()
        await session.refresh(workflow, ["actions"])
        return workflow

    @staticmethod
    async def get_workflows(session: AsyncSession, org_id: str | UUID) -> list[Workflow]:
        result = await session.execute(
            select(Workflow)
            .where(Workflow.organization_id == str(org_id), Workflow.deleted_at.is_(None))
            .options(selectinload(Workflow.actions))
            .order_by(Workflow.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_workflow(
        session: AsyncSession, org_id: str | UUID, workflow_id: str | UUID
    ) -> Workflow:
        result = await session.execute(
            select(Workflow)
            .where(
                Workflow.id == str(workflow_id),
                Workflow.organization_id == str(org_id),
                Workflow.deleted_at.is_(None),
            )
            .options(selectinload(Workflow.actions))
        )
        workflow = result.scalars().first()
        if not workflow:
            raise SaaSForgeError("Workflow not found", status_code=404)
        return workflow


class WorkflowEngine:
    """Core automation engine."""

    @staticmethod
    async def trigger_event(
        session: AsyncSession, org_id: str | UUID, trigger_type: str, payload: dict[str, Any]
    ):
        """Finds active workflows matching the trigger_type and executes their actions."""
        # Note: In production this would directly queue a Celery task to avoid blocking HTTP.
        # But for this implementation, we will fetch matching workflows and then queue execution.
        result = await session.execute(
            select(Workflow)
            .where(
                Workflow.organization_id == str(org_id),
                Workflow.trigger_type == trigger_type,
                Workflow.is_active == True,
                Workflow.deleted_at.is_(None),
            )
            .options(selectinload(Workflow.actions))
        )
        workflows = result.scalars().all()

        for workflow in workflows:
            # Enqueue the workflow execution in Celery
            execute_workflow_task.delay(workflow.id, payload)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
@async_task
async def execute_workflow_task(self, workflow_id: str, payload: dict[str, Any]):
    from app.db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Workflow)
            .where(Workflow.id == workflow_id)
            .options(selectinload(Workflow.actions))
        )
        workflow = result.scalars().first()

        if not workflow or not workflow.is_active:
            return

        actions = sorted(workflow.actions, key=lambda a: a.order)
        for action in actions:
            try:
                await execute_action(session, action, payload)
            except Exception as e:
                # Execution failed
                raise self.retry(exc=e)


async def execute_action(session: AsyncSession, action: WorkflowAction, payload: dict[str, Any]):
    """Execute a single workflow action."""
    # This is a naive stub engine. A real engine would interpolate payload variables (e.g. {{task.title}}).
    if action.action_type == "webhook":
        # Simplified example
        pass
    elif action.action_type == "create_task":
        from app.models.task import Task

        # Example of creating a task automatically
        project_id = action.config.get("project_id")
        if project_id:
            task = Task(
                project_id=project_id,
                title=action.config.get("title", "Automated Task"),
                description=action.config.get("description", ""),
                status="todo",
            )
            session.add(task)
            await session.commit()
    # Add more actions (email, slack, etc.)
