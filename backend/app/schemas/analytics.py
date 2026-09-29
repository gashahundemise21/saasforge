from pydantic import BaseModel, ConfigDict

from app.schemas.audit_log import AuditLogResponse


class DashboardStatsResponse(BaseModel):
    total_projects: int
    total_tasks: int
    tasks_by_status: dict[str, int]
    recent_activity: list[AuditLogResponse]

    model_config = ConfigDict(from_attributes=True)
