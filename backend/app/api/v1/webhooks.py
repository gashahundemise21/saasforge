from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentOrganization, RequireRole, SessionDep
from app.schemas.webhook import (
    WebhookDeliveryResponse,
    WebhookEndpointCreate,
    WebhookEndpointCreateResponse,
    WebhookEndpointResponse,
)
from app.services.webhook import WebhookEndpointService
from app.services.audit_log import AuditLogService
from app.api.deps import CurrentActor

router = APIRouter()


@router.post(
    "",
    response_model=WebhookEndpointCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_webhook(
    session: SessionDep,
    current_org: CurrentOrganization,
    current_actor: CurrentActor,
    webhook_in: WebhookEndpointCreate,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> WebhookEndpointCreateResponse:
    """Create a new webhook endpoint. Returns the secret once."""
    endpoint = await WebhookEndpointService.create_endpoint(session, current_org.id, webhook_in)
    await AuditLogService.log_action(session, current_org.id, current_actor, 'create', 'webhook', endpoint.id, {'url': endpoint.url, 'events': endpoint.events})

    # Dump attributes and merge with secret
    response_data = WebhookEndpointResponse.model_validate(endpoint).model_dump()
    response_data["secret"] = endpoint.secret
    return WebhookEndpointCreateResponse(**response_data)


@router.get("", response_model=list[WebhookEndpointResponse])
async def list_webhooks(
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> list[WebhookEndpointResponse]:
    """Get all webhooks for the organization."""
    return await WebhookEndpointService.get_org_endpoints(session, current_org.id)  # type: ignore


@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    session: SessionDep,
    current_org: CurrentOrganization,
    current_actor: CurrentActor,
    endpoint_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> None:
    """Delete a webhook endpoint."""
    await WebhookEndpointService.delete_endpoint(session, current_org.id, endpoint_id)
    await AuditLogService.log_action(session, current_org.id, current_actor, 'delete', 'webhook', endpoint_id)


@router.get("/{endpoint_id}/deliveries", response_model=list[WebhookDeliveryResponse])
async def list_webhook_deliveries(
    session: SessionDep,
    current_org: CurrentOrganization,
    endpoint_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> list[WebhookDeliveryResponse]:
    """Get delivery history for a webhook endpoint."""
    return await WebhookEndpointService.list_deliveries(session, current_org.id, endpoint_id)  # type: ignore


@router.post("/{endpoint_id}/deliveries/{delivery_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def replay_webhook_delivery(
    session: SessionDep,
    current_org: CurrentOrganization,
    endpoint_id: UUID,
    delivery_id: UUID,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> None:
    """Replay a specific webhook delivery."""
    await WebhookEndpointService.replay_delivery(session, current_org.id, endpoint_id, delivery_id)
