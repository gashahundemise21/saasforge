from fastapi import APIRouter, Depends

from app.api.deps import CurrentOrganization, RequireRole, SessionDep
from app.schemas.analytics import DashboardStatsResponse
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> DashboardStatsResponse:
    """Get dashboard analytics for the organization."""
    return await AnalyticsService.get_dashboard_stats(session, current_org.id)
