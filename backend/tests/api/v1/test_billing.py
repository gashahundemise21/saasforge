from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.fixture
def mock_stripe():
    with patch("app.services.billing.stripe") as mock:
        yield mock


@pytest.mark.asyncio
async def test_create_checkout_session(auth_client: AsyncClient, mock_stripe: MagicMock):
    # Setup Org
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Billing Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Mock stripe customer and checkout
    mock_stripe.Customer.create.return_value = MagicMock(id="cus_test123")
    mock_stripe.checkout.Session.create.return_value = MagicMock(
        url="https://checkout.stripe.com/test"
    )

    # Create checkout
    resp = await auth_client.post(
        "/api/v1/billing/checkout",
        json={
            "plan_id": "price_premium",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["url"] == "https://checkout.stripe.com/test"

    # Verify Customer.create was called
    mock_stripe.Customer.create.assert_called_once()
    assert mock_stripe.Customer.create.call_args[1]["name"] == "Billing Org"

    # Verify Session.create was called
    mock_stripe.checkout.Session.create.assert_called_once()
    call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
    assert call_kwargs["customer"] == "cus_test123"
    assert call_kwargs["line_items"][0]["price"] == "price_premium"


@pytest.mark.asyncio
async def test_stripe_webhook_subscription_updated(
    auth_client: AsyncClient, mock_stripe: MagicMock
):
    # Setup Org
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Webhook Org"})
    org = org_resp.json()

    # We need to manually set the stripe_customer_id in DB to match the webhook,
    # or just trigger a checkout first to set it.
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})
    mock_stripe.Customer.create.return_value = MagicMock(id="cus_wh_123")
    mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://test")
    await auth_client.post(
        "/api/v1/billing/checkout",
        json={"plan_id": "price_123", "success_url": "http://test", "cancel_url": "http://test"},
    )

    # Prepare webhook payload
    payload = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_wh_123",
                "status": "active",
                "items": {"data": [{"price": {"id": "price_pro"}}]},
            }
        },
    }

    # Mock the Webhook signature verifier to return the payload instead of throwing
    mock_stripe.Webhook.construct_event.return_value = payload

    # Post webhook
    resp = await auth_client.post(
        "/api/v1/billing/webhook",
        json=payload,
        headers={"Stripe-Signature": "t=123,v1=signature_test"},
    )
    assert resp.status_code == 200

    # Fetch org and verify subscription status is updated
    org_fetch = await auth_client.get("/api/v1/organizations/me")
    org_updated = next(o for o in org_fetch.json() if o["id"] == org["id"])
    assert org_updated["plan_id"] == "price_pro"
    assert org_updated["subscription_status"] == "active"
