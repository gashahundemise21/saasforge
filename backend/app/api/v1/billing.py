from typing import Any

from fastapi import APIRouter, Depends, Header, Request, status
from pydantic import BaseModel

from app.api.deps import CurrentOrganization, RequireRole, SessionDep
from app.services.billing import BillingService
from app.schemas.billing import InvoiceResponse, SubscriptionDetailsResponse


router = APIRouter()


class CheckoutRequest(BaseModel):
    plan_id: str
    success_url: str
    cancel_url: str


class PortalRequest(BaseModel):
    return_url: str


class SessionUrlResponse(BaseModel):
    url: str


@router.post("/checkout", response_model=SessionUrlResponse)
async def create_checkout_session(
    session: SessionDep,
    current_org: CurrentOrganization,
    request: CheckoutRequest,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> SessionUrlResponse:
    """Create a Stripe Checkout Session to upgrade the organization's plan."""
    url = await BillingService.create_checkout_session(
        session, current_org.id, request.plan_id, request.success_url, request.cancel_url
    )
    return SessionUrlResponse(url=url)


@router.post("/portal", response_model=SessionUrlResponse)
async def create_portal_session(
    session: SessionDep,
    current_org: CurrentOrganization,
    request: PortalRequest,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> SessionUrlResponse:
    """Create a Stripe Customer Portal Session for billing management."""
    url = await BillingService.create_portal_session(session, current_org.id, request.return_url)
    return SessionUrlResponse(url=url)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    session: SessionDep,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
) -> dict[str, Any]:
    """
    Stripe Webhook Endpoint.
    Receives events from Stripe securely using signature verification.
    """
    payload = await request.body()
    await BillingService.process_webhook(session, payload, stripe_signature)
    return {"received": True}


@router.get("/invoices", response_model=list[InvoiceResponse])
async def get_invoices(
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> list[dict]:
    """Get all invoices for the organization."""
    return await BillingService.get_invoices(session, current_org.id)

@router.get("/subscription", response_model=SubscriptionDetailsResponse)
async def get_subscription(
    session: SessionDep,
    current_org: CurrentOrganization,
    _req: Depends = Depends(RequireRole(["Owner", "Admin"])),
) -> dict:
    """Get current subscription details for the organization."""
    details = await BillingService.get_subscription_details(session, current_org.id)
    if not details:
        # Return a 404 or a mock free-tier representation
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No active subscription found")
    return details
