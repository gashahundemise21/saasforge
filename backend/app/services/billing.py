from typing import Any
from uuid import UUID

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError, SaaSForgeError
from app.models.organization import Organization

# Configure Stripe
stripe.api_key = settings.STRIPE_API_KEY


class BillingService:
    @staticmethod
    async def create_checkout_session(
        session: AsyncSession, org_id: str | UUID, plan_id: str, success_url: str, cancel_url: str
    ) -> str:
        """Create a Stripe Checkout Session to upgrade an organization."""
        org = await BillingService._get_org(session, org_id)

        # In a real app, map the plan_id to a Stripe Price ID here
        # E.g., price_id = settings.STRIPE_PRICE_IDS[plan_id]
        # For demonstration, we assume plan_id *is* the price_id or we just hardcode one
        price_id = plan_id  # Mocking this

        # Create or retrieve customer
        customer_id = org.stripe_customer_id
        if not customer_id:
            customer = stripe.Customer.create(
                name=org.name,
                metadata={"org_id": str(org.id)},
            )
            customer_id = customer.id
            org.stripe_customer_id = customer_id
            await session.commit()

        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(org.id),
        )
        return checkout_session.url  # type: ignore

    @staticmethod
    async def create_portal_session(session: AsyncSession, org_id: str | UUID, return_url: str) -> str:
        """Create a Stripe Customer Portal Session for managing billing."""
        org = await BillingService._get_org(session, org_id)

        if not org.stripe_customer_id:
            raise SaaSForgeError("Organization does not have a billing customer associated.", code="NO_BILLING_CUSTOMER", status_code=400)

        portal_session = stripe.billing_portal.Session.create(
            customer=org.stripe_customer_id,
            return_url=return_url,
        )
        return portal_session.url  # type: ignore

    @staticmethod
    async def process_webhook(session: AsyncSession, payload: bytes, sig_header: str) -> None:
        """Process an incoming Stripe webhook."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise SaaSForgeError(f"Invalid payload: {e}", status_code=400)
        except stripe.error.SignatureVerificationError as e:  # type: ignore
            raise SaaSForgeError(f"Invalid signature: {e}", status_code=400)

        # Handle the event
        if event["type"] == "customer.subscription.created" or event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            await BillingService._sync_subscription(session, subscription)
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            await BillingService._sync_subscription(session, subscription)

    @staticmethod
    async def _sync_subscription(session: AsyncSession, subscription: dict[str, Any]) -> None:
        """Sync a Stripe subscription object to our Organization model."""
        customer_id = subscription["customer"]
        status = subscription["status"]
        subscription_id = subscription["id"]

        # Find org by customer_id
        result = await session.execute(
            select(Organization).where(Organization.stripe_customer_id == customer_id)
        )
        org = result.scalars().first()
        if not org:
            # Maybe the customer was created out-of-band or org was deleted
            return

        org.stripe_subscription_id = subscription_id
        org.subscription_status = status

        # If there's an item, update the plan
        items = subscription.get("items", {}).get("data", [])
        if items:
            org.plan_id = items[0]["price"]["id"]
        
        # If deleted/canceled, fallback to free
        if status in ["canceled", "unpaid"]:
            org.plan_id = "free"

        await session.commit()

    @staticmethod
    async def _get_org(session: AsyncSession, org_id: str | UUID) -> Organization:
        result = await session.execute(select(Organization).where(Organization.id == str(org_id)))
        org = result.scalars().first()
        if not org:
            raise NotFoundError("Organization")
        return org
