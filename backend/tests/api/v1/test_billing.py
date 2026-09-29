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


@pytest.mark.asyncio
async def test_get_invoices_and_subscription(auth_client: AsyncClient, mock_stripe: MagicMock):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Invoice Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Checkout first to set customer ID
    mock_stripe.Customer.create.return_value = MagicMock(id="cus_inv_123")
    mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://test")
    await auth_client.post(
        "/api/v1/billing/checkout",
        json={"plan_id": "price_123", "success_url": "http://test", "cancel_url": "http://test"},
    )
    
    # Send webhook to set subscription ID
    payload = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_inv_123",
                "customer": "cus_inv_123",
                "status": "active",
                "items": {"data": [{"price": {"id": "price_123"}}]},
            }
        },
    }
    mock_stripe.Webhook.construct_event.return_value = payload
    await auth_client.post(
        "/api/v1/billing/webhook",
        json=payload,
        headers={"Stripe-Signature": "t=123,v1=signature_test"},
    )

    # Mock invoices
    class MockInvoice:
        def __init__(self):
            self.id = "in_123"
            self.amount_due = 1000
            self.amount_paid = 1000
            self.amount_remaining = 0
            self.status = "paid"
            self.created = 1630000000
            self.hosted_invoice_url = "http://stripe/in"
            self.invoice_pdf = "http://stripe/pdf"
    
    class MockList:
        def auto_paging_iter(self):
            yield MockInvoice()
            
    mock_stripe.Invoice.list.return_value = MockList()
    
    inv_res = await auth_client.get("/api/v1/billing/invoices")
    assert inv_res.status_code == 200
    invoices = inv_res.json()
    assert len(invoices) == 1
    assert invoices[0]["id"] == "in_123"

    # Mock subscription details
    class MockPrice:
        def __init__(self):
            self.id = "price_123"
            self.unit_amount = 1000
            self.currency = "usd"
            
    class MockSubItem:
        def __init__(self):
            self.price = MockPrice()
            
    class MockSubItemsList:
        def __init__(self):
            self.data = [MockSubItem()]

    class MockSubscription:
        def __init__(self):
            self.id = "sub_inv_123"
            self.status = "active"
            self.current_period_start = 1630000000
            self.current_period_end = 1632592000
            self.cancel_at_period_end = False
            self.items = MockSubItemsList()
            
    mock_stripe.Subscription.retrieve.return_value = MockSubscription()

    sub_res = await auth_client.get("/api/v1/billing/subscription")
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["id"] == "sub_inv_123"
    assert sub_data["plan_id"] == "price_123"
