import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_audit_logs_lifecycle(auth_client: AsyncClient):
    # Setup organization
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Audit Log Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Trigger action: create a project
    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Audited Project"})
    assert proj_resp.status_code == 201

    # Wait briefly for BackgroundTasks to commit to the DB
    import asyncio
    await asyncio.sleep(0.1)

    # Fetch audit logs
    logs_resp = await auth_client.get("/api/v1/audit-logs")
    assert logs_resp.status_code == 200
    
    logs = logs_resp.json()
    assert len(logs) == 1
    
    log = logs[0]
    assert log["organization_id"] == org["id"]
    assert log["action"] == "project.created"
    assert log["resource_type"] == "project"
    assert log["actor_type"] == "user"
    assert log["details"]["name"] == "Audited Project"

    # Trigger action: update a project
    proj_id = proj_resp.json()["id"]
    update_resp = await auth_client.patch(f"/api/v1/projects/{proj_id}", json={"name": "Updated Audited Project"})
    assert update_resp.status_code == 200
    
    await asyncio.sleep(0.1)
    
    # Fetch audit logs again
    logs_resp = await auth_client.get("/api/v1/audit-logs")
    logs = logs_resp.json()
    
    # order is descending, so latest is first
    assert len(logs) == 2
    assert logs[0]["action"] == "project.updated"
    assert logs[0]["details"]["name"] == "Updated Audited Project"
