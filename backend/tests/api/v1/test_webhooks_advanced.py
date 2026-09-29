import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import respx

@pytest.mark.asyncio
@respx.mock
async def test_webhooks_advanced(auth_client: AsyncClient, db_session: AsyncSession):
    # 1. Create org
    org_res = await auth_client.post(
        "/api/v1/organizations", json={"name": "Webhook Org"}
    )
    assert org_res.status_code == 201
    org_slug = org_res.json()["slug"]
    
    # Mock the external webhook URL
    respx.post("https://example.com/webhook").mock(return_value=respx.MockResponse(200))
    
    # 2. Create Webhook
    wh_res = await auth_client.post(
        "/api/v1/webhooks",
        json={"url": "https://example.com/webhook", "events": ["task.*"]},
        headers={"X-Organization-Slug": org_slug}
    )
    assert wh_res.status_code == 201
    endpoint_id = wh_res.json()["id"]
    secret = wh_res.json()["secret"]
    assert secret.startswith("whsec_")
    
    # 3. Create a Task to trigger webhook
    from app.services.webhook import WebhookDispatcher
    await WebhookDispatcher.dispatch_event(
        session=db_session,
        org_id=org_res.json()["id"],
        event_type="task.created",
        payload={"task_id": "123"}
    )
    await db_session.commit()
    
    # 4. List Deliveries
    deliv_res = await auth_client.get(
        f"/api/v1/webhooks/{endpoint_id}/deliveries",
        headers={"X-Organization-Slug": org_slug}
    )
    assert deliv_res.status_code == 200
    deliveries = deliv_res.json()
    assert len(deliveries) >= 1
    delivery_id = deliveries[0]["id"]
    
    # 5. Retry Delivery
    retry_res = await auth_client.post(
        f"/api/v1/webhooks/{endpoint_id}/deliveries/{delivery_id}/retry",
        headers={"X-Organization-Slug": org_slug}
    )
    assert retry_res.status_code == 202
    
    # 6. Check Deliveries Again (should have 2 now)
    deliv_res2 = await auth_client.get(
        f"/api/v1/webhooks/{endpoint_id}/deliveries",
        headers={"X-Organization-Slug": org_slug}
    )
    assert len(deliv_res2.json()) == len(deliveries) + 1
