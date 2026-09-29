import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_analytics(auth_client: AsyncClient):
    # Setup Org
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Analytics Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Create 1 project
    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Proj 1", "description": ""})
    proj_id = proj_resp.json()["id"]

    # Create 3 tasks (1 todo, 2 in_progress)
    await auth_client.post(
        f"/api/v1/projects/{proj_id}/tasks", 
        json={"title": "T1"}
    )
    
    t2_resp = await auth_client.post(
        f"/api/v1/projects/{proj_id}/tasks", 
        json={"title": "T2"}
    )
    await auth_client.patch(
        f"/api/v1/tasks/{t2_resp.json()['id']}", 
        json={"status": "in_progress"}
    )
    
    t3_resp = await auth_client.post(
        f"/api/v1/projects/{proj_id}/tasks", 
        json={"title": "T3"}
    )
    await auth_client.patch(
        f"/api/v1/tasks/{t3_resp.json()['id']}", 
        json={"status": "in_progress"}
    )

    # Fetch analytics
    resp = await auth_client.get("/api/v1/analytics/dashboard")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_projects"] == 1
    assert data["total_tasks"] == 3
    assert data["tasks_by_status"]["todo"] == 1
    assert data["tasks_by_status"]["in_progress"] == 2
    
    # Check that audit logs were populated
    assert len(data["recent_activity"]) > 0
    assert data["recent_activity"][0]["action"] == "task.updated"
