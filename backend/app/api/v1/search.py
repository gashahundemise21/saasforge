from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentOrganization, RequireRole, SessionDep
from app.schemas.search import SearchResponse
from app.services.search import SearchService

router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search_organization(
    session: SessionDep,
    current_org: CurrentOrganization,
    q: str = Query(..., min_length=1, description="Search query"),
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> SearchResponse:
    """Search for resources within an organization."""
    return await SearchService.search(session, current_org.id, q)
