import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

async def test_notifications_lifecycle(auth_client: AsyncClient, test_user: dict, db_session: AsyncSession):
    # 1. Create org
    res = await auth_client.post("/api/v1/organizations", json={"name": "Notif Org"})
    org = res.json()
    org_slug = org["slug"]
    org_id = org["id"]
    
    # 2. Get unread count initially (should be 0)
    res = await auth_client.get(
        "/api/v1/notifications/unread-count",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 200
    assert res.json()["unread_count"] == 0
    
    # 3. Create a notification directly using the service
    from app.services.notification import NotificationService
    
    notif = await NotificationService.create_notification(
        session=db_session,
        user_id=test_user.id,
        organization_id=org_id,
        title="Test Notification",
        message="This is a test",
        type="system",
        action_url="/dashboard"
    )
    notif_id = str(notif.id)
    
    # 4. Get unread count (should be 1)
    res = await auth_client.get(
        "/api/v1/notifications/unread-count",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 200
    assert res.json()["unread_count"] == 1
    
    # 5. List notifications
    res = await auth_client.get(
        "/api/v1/notifications",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 200
    notifs = res.json()
    assert len(notifs) == 1
    assert notifs[0]["id"] == notif_id
    assert notifs[0]["read_at"] is None
    
    # 6. Mark as read
    res = await auth_client.put(
        f"/api/v1/notifications/{notif_id}/read",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 200
    assert res.json()["read_at"] is not None
    
    # 7. Unread count should be 0 again
    res = await auth_client.get(
        "/api/v1/notifications/unread-count",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 200
    assert res.json()["unread_count"] == 0

    # 8. Create another notification and mark all as read
    await NotificationService.create_notification(
        session=db_session,
        user_id=test_user.id,
        organization_id=org_id,
        title="Test Notification 2",
        message="This is another test",
        type="system"
    )
        
    res = await auth_client.put(
        "/api/v1/notifications/read-all",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 204
    
    res = await auth_client.get(
        "/api/v1/notifications/unread-count",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 200
    assert res.json()["unread_count"] == 0
