from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_utc_now
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    @staticmethod
    async def create_project(
        session: AsyncSession, org_id: str | UUID, project_in: ProjectCreate
    ) -> Project:
        """Create a new project for an organization."""
        project = Project(
            organization_id=str(org_id),
            name=project_in.name,
            description=project_in.description,
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

    @staticmethod
    async def get_org_projects(session: AsyncSession, org_id: str | UUID) -> list[Project]:
        """Get all active projects for an organization."""
        result = await session.execute(
            select(Project)
            .where(Project.organization_id == str(org_id))
            .where(Project.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_project(session: AsyncSession, org_id: str | UUID, project_id: str | UUID) -> Project:
        """Get a specific project."""
        result = await session.execute(
            select(Project)
            .where(Project.id == str(project_id))
            .where(Project.organization_id == str(org_id))
            .where(Project.deleted_at.is_(None))
        )
        project = result.scalars().first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    @staticmethod
    async def update_project(
        session: AsyncSession, org_id: str | UUID, project_id: str | UUID, project_in: ProjectUpdate
    ) -> Project:
        """Update a project."""
        project = await ProjectService.get_project(session, org_id, project_id)
        
        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
            
        await session.commit()
        await session.refresh(project)
        return project

    @staticmethod
    async def delete_project(session: AsyncSession, org_id: str | UUID, project_id: str | UUID) -> None:
        """Soft delete a project."""
        project = await ProjectService.get_project(session, org_id, project_id)
        project.deleted_at = get_utc_now()
        await session.commit()
