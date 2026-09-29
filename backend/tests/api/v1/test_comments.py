import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_comment(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Comment 1"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Project 1", "key": "PRJ"})
    project = proj_resp.json()

    task_resp = await auth_client.post(f"/api/v1/projects/{project['id']}/tasks", json={"title": "Task", "description": "desc"})
    task = task_resp.json()

    response = await auth_client.post(
        "/api/v1/comments",
        json={
            "task_id": task["id"],
            "content": "This is a test comment",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "This is a test comment"
    assert data["task_id"] == task["id"]
    assert "author" in data

async def test_get_task_comments(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Comment 2"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Project 2", "key": "PRJ2"})
    project = proj_resp.json()

    task_resp = await auth_client.post(f"/api/v1/projects/{project['id']}/tasks", json={"title": "Task", "description": "desc"})
    task = task_resp.json()

    await auth_client.post("/api/v1/comments", json={"task_id": task["id"], "content": "Comment 1"})
    await auth_client.post("/api/v1/comments", json={"task_id": task["id"], "content": "Comment 2"})

    response = await auth_client.get(f"/api/v1/comments/tasks/{task['id']}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["content"] == "Comment 1"
    assert data[1]["content"] == "Comment 2"

async def test_update_comment(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Comment 3"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Project 3", "key": "PRJ3"})
    project = proj_resp.json()

    task_resp = await auth_client.post(f"/api/v1/projects/{project['id']}/tasks", json={"title": "Task", "description": "desc"})
    task = task_resp.json()

    comment_resp = await auth_client.post("/api/v1/comments", json={"task_id": task["id"], "content": "Original"})
    comment = comment_resp.json()

    response = await auth_client.put(
        f"/api/v1/comments/{comment['id']}",
        json={"content": "Updated"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Updated"

async def test_delete_comment(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Comment 4"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Project 4", "key": "PRJ4"})
    project = proj_resp.json()

    task_resp = await auth_client.post(f"/api/v1/projects/{project['id']}/tasks", json={"title": "Task", "description": "desc"})
    task = task_resp.json()

    comment_resp = await auth_client.post("/api/v1/comments", json={"task_id": task["id"], "content": "To be deleted"})
    comment = comment_resp.json()

    response = await auth_client.delete(f"/api/v1/comments/{comment['id']}")
    assert response.status_code == 204

    # Verify it's deleted (soft delete)
    get_response = await auth_client.get(f"/api/v1/comments/tasks/{task['id']}")
    assert len(get_response.json()) == 0
