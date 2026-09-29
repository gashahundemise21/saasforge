import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Task"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Proj Task"})
    proj = proj_resp.json()

    task_resp = await auth_client.post(
        f"/api/v1/projects/{proj['id']}/tasks",
        json={"title": "My Task", "description": "Do something"},
    )
    assert task_resp.status_code == 201
    task = task_resp.json()
    assert task["title"] == "My Task"
    assert task["status"] == "todo"


@pytest.mark.asyncio
async def test_update_task_assignee(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Assign"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Proj Assign"})
    proj = proj_resp.json()

    task_resp = await auth_client.post(
        f"/api/v1/projects/{proj['id']}/tasks", json={"title": "Assign Task"}
    )
    task = task_resp.json()

    # Get current user
    me_resp = await auth_client.get("/api/v1/users/me")
    me = me_resp.json()

    update_resp = await auth_client.patch(
        f"/api/v1/tasks/{task['id']}", json={"assignee_id": me["id"], "status": "in_progress"}
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["assignee_id"] == me["id"]
    assert updated["status"] == "in_progress"
