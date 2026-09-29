from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentActor, CurrentOrganization, RequireRole, SessionDep
from app.models.user import User
from app.schemas.integration import (
    IntegrationConnectionCreate,
    IntegrationConnectionResponse,
    IntegrationConnectionUpdate,
)
from app.services.integration import IntegrationService

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("", response_model=IntegrationConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    *,
    db: SessionDep,
    current_org: CurrentOrganization,
    integration_in: IntegrationConnectionCreate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> IntegrationConnectionResponse:
    """Create a new integration connection."""
    service = IntegrationService(db)
    return await service.create_connection(current_org.id, integration_in)


@router.get("", response_model=list[IntegrationConnectionResponse])
async def list_integrations(
    *,
    db: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> list[IntegrationConnectionResponse]:
    """List all integrations for the organization."""
    service = IntegrationService(db)
    return await service.get_connections(current_org.id)


@router.get("/{integration_id}", response_model=IntegrationConnectionResponse)
async def get_integration(
    *,
    db: SessionDep,
    integration_id: str,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin", "Member"])),
) -> IntegrationConnectionResponse:
    """Get a specific integration connection."""
    service = IntegrationService(db)
    connection = await service.get_connection(current_org.id, integration_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Integration not found")
    return connection


@router.patch("/{integration_id}", response_model=IntegrationConnectionResponse)
async def update_integration(
    *,
    db: SessionDep,
    integration_id: str,
    integration_in: IntegrationConnectionUpdate,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> IntegrationConnectionResponse:
    """Update an integration connection."""
    service = IntegrationService(db)
    return await service.update_connection(current_org.id, integration_id, integration_in)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    *,
    db: SessionDep,
    integration_id: str,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
):
    """Delete an integration connection."""
    service = IntegrationService(db)
    await service.delete_connection(current_org.id, integration_id)
