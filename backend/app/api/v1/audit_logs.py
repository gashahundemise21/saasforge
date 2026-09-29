from fastapi import APIRouter, Depends

from app.api.deps import CurrentOrganization, RequireRole, SessionDep
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_log import AuditLogService

router = APIRouter()


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    session: SessionDep,
    current_org: CurrentOrganization,
    limit: int = 100,
    skip: int = 0,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> list[AuditLogResponse]:
    """
    Get audit logs for the organization.
    Requires Admin or Owner role.
    """
    return await AuditLogService.list_logs(session, current_org.id, limit=limit, skip=skip)  # type: ignore
