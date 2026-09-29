import hmac

import pytest
import respx
from httpx import AsyncClient, Response

from app.services.webhook import WebhookDispatcher


@pytest.mark.asyncio
async def test_create_and_list_webhooks(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Webhook Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Create webhook
    wh_resp = await auth_client.post(
        "/api/v1/webhooks",
        json={"url": "https://example.com/webhook", "events": ["project.created"]},
    )
    assert wh_resp.status_code == 201
    wh_data = wh_resp.json()
    assert wh_data["url"] == "https://example.com/webhook"
    assert "secret" in wh_data

    # List webhooks
    list_resp = await auth_client.get("/api/v1/webhooks")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


@pytest.mark.asyncio
@respx.mock
async def test_webhook_delivery(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Delivery Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Create webhook
    wh_resp = await auth_client.post(
        "/api/v1/webhooks", json={"url": "https://example.com/webhook", "events": ["project.*"]}
    )
    wh_data = wh_resp.json()
    secret = wh_data["secret"]

    # Mock the external webhook destination
    request = respx.post("https://example.com/webhook").mock(return_value=Response(200))

    # Trigger action: create a project (which triggers the webhook)
    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Webhook Project"})
    assert proj_resp.status_code == 201

    # In tests without an event loop running forever, BackgroundTasks execute right after response.
    # We should have hit the mock.
    assert request.called
    assert request.call_count == 1

    req = request.calls.last.request
    assert req.headers["X-SaaSForge-Event"] == "project.created"

    # Verify HMAC signature
    signature = req.headers["X-SaaSForge-Signature"]
    expected_signature = WebhookDispatcher._generate_signature(secret, req.content)
    assert hmac.compare_digest(signature, expected_signature)

    # Wait a tiny bit for the DB insert of the delivery
    import asyncio

    await asyncio.sleep(0.1)

    # Check delivery log
    del_resp = await auth_client.get(f"/api/v1/webhooks/{wh_data['id']}/deliveries")
    assert del_resp.status_code == 200
    deliveries = del_resp.json()
    assert len(deliveries) == 1
    assert deliveries[0]["success"] is True
    assert deliveries[0]["status_code"] == 200
    assert deliveries[0]["event_type"] == "project.created"
