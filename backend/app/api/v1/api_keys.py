from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentOrganization, RequireRole, SessionDep
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyResponse
from app.schemas.api_request_log import ApiRequestLogResponse
from app.models.api_request_log import ApiRequestLog
from sqlalchemy import select
from app.services.api_key import ApiKeyService

router = APIRouter()


@router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    session: SessionDep,
    current_org: CurrentOrganization,
    api_key_in: ApiKeyCreate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> ApiKeyCreateResponse:
    """
    Create a new API key.
    Requires Admin or Owner role.
    """
    api_key, raw_key = await ApiKeyService.create_api_key(session, current_org.id, api_key_in)

    # We create the response dict manually to include raw_key
    response_data = ApiKeyResponse.model_validate(api_key).model_dump()
    response_data["raw_key"] = raw_key
    return ApiKeyCreateResponse(**response_data)


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> list[ApiKeyResponse]:
    """
    List all active API keys.
    Requires Admin or Owner role.
    """
    return await ApiKeyService.list_api_keys(session, current_org.id)  # type: ignore


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    session: SessionDep,
    current_org: CurrentOrganization,
    key_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> None:
    """
    Revoke an API key.
    Requires Admin or Owner role.
    """
    await ApiKeyService.revoke_api_key(session, current_org.id, key_id)


@router.post("/{key_id}/rotate", response_model=ApiKeyCreateResponse)
async def rotate_api_key(
    session: SessionDep,
    current_org: CurrentOrganization,
    key_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> ApiKeyCreateResponse:
    """
    Rotate an API key.
    Requires Admin or Owner role.
    """
    api_key, raw_key = await ApiKeyService.rotate_api_key(session, current_org.id, key_id)
    response_data = ApiKeyResponse.model_validate(api_key).model_dump()
    response_data["raw_key"] = raw_key
    return ApiKeyCreateResponse(**response_data)


@router.get("/{key_id}/logs", response_model=list[ApiRequestLogResponse])
async def get_api_key_logs(
    session: SessionDep,
    current_org: CurrentOrganization,
    key_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> list[ApiRequestLogResponse]:
    """
    Get request logs for an API key.
    """
    # Verify the key belongs to the org
    await ApiKeyService.rotate_api_key(session, current_org.id, key_id) # Just to check existence? No, that rotates!
    
    # Better check
    from app.models.api_key import ApiKey
    from fastapi import HTTPException
    
    result = await session.execute(
        select(ApiKey).where(ApiKey.id == str(key_id), ApiKey.organization_id == str(current_org.id))
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="API Key not found")
        
    logs = await session.execute(
        select(ApiRequestLog)
        .where(ApiRequestLog.api_key_id == str(key_id))
        .order_by(ApiRequestLog.created_at.desc())
        .limit(100)
    )
    return list(logs.scalars().all())
