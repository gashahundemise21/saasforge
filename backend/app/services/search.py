from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.task import Task
from app.models.user import OrganizationUser, User
from app.schemas.search import SearchResponse, SearchResult


class SearchService:
    @staticmethod
    async def search(session: AsyncSession, org_id: str | UUID, query: str) -> SearchResponse:
        results: list[SearchResult] = []
        if not query or len(query) < 2:
            return SearchResponse(query=query, results=[], total=0)

        search_pattern = f"%{query}%"

        # Search Projects
        projects_stmt = (
            select(Project)
            .where(
                Project.organization_id == str(org_id),
                or_(Project.name.ilike(search_pattern), Project.description.ilike(search_pattern)),
            )
            .limit(10)
        )

        projects_result = await session.execute(projects_stmt)
        for project in projects_result.scalars().all():
            results.append(
                SearchResult(
                    id=UUID(project.id),
                    type="project",
                    title=project.name,
                    description=project.description,
                    url=f"/dashboard/projects/{project.id}",
                )
            )

        # Search Tasks
        # Tasks belong to projects which belong to the org
        tasks_stmt = (
            select(Task)
            .join(Project, Task.project_id == Project.id)
            .where(
                Project.organization_id == str(org_id),
                or_(Task.title.ilike(search_pattern), Task.description.ilike(search_pattern)),
            )
            .limit(10)
        )
        tasks_result = await session.execute(tasks_stmt)
        for task in tasks_result.scalars().all():
            results.append(
                SearchResult(
                    id=UUID(task.id),
                    type="task",
                    title=task.title,
                    description=task.description,
                    url=f"/dashboard/projects/{task.project_id}/tasks/{task.id}",
                )
            )

        # Search Users
        users_stmt = (
            select(User)
            .join(OrganizationUser, User.id == OrganizationUser.user_id)
            .where(
                OrganizationUser.organization_id == str(org_id),
                User.email.ilike(search_pattern),
            )
            .limit(10)
        )
        users_result = await session.execute(users_stmt)
        for user in users_result.scalars().all():
            results.append(
                SearchResult(
                    id=UUID(user.id),
                    type="user",
                    title=user.email,
                    description=user.email,
                    url="/dashboard/settings/team",
                )
            )

        return SearchResponse(query=query, results=results, total=len(results))
