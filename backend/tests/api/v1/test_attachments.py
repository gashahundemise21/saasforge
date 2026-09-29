import pytest
from httpx import AsyncClient
import io

pytestmark = pytest.mark.asyncio

async def test_create_and_get_attachment(auth_client: AsyncClient, test_user: dict):
    # Create org
    res = await auth_client.post("/api/v1/organizations", json={"name": "Att Org"})
    org = res.json()
    org_slug = org["slug"]
    
    # Create project
    res = await auth_client.post(
        "/api/v1/projects", 
        json={"name": "Att Project"},
        headers={"X-Organization-Slug": org_slug}
    )
    project = res.json()
    project_id = project["id"]
    
    # Create task
    res = await auth_client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Att Task"},
        headers={"X-Organization-Slug": org_slug}
    )
    task = res.json()
    task_id = task["id"]
    
    # Upload attachment
    file_content = b"test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    data = {"task_id": task_id}
    
    res = await auth_client.post(
        "/api/v1/attachments",
        files=files,
        data=data,
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 200
    attachment = res.json()
    assert attachment["filename"] == "test.txt"
    assert attachment["size"] == len(file_content)
    
    att_id = attachment["id"]
    
    # List attachments
    res = await auth_client.get(
        f"/api/v1/attachments/tasks/{task_id}",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 200
    attachments = res.json()
    assert len(attachments) == 1
    assert attachments[0]["id"] == att_id
    
    # Download attachment
    res = await auth_client.get(
        f"/api/v1/attachments/{att_id}/download",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 200
    assert res.content == file_content
    
    # Delete attachment
    res = await auth_client.delete(
        f"/api/v1/attachments/{att_id}",
        headers={"X-Organization-Slug": org_slug}
    )
    assert res.status_code == 204
    
    # List again
    res = await auth_client.get(
        f"/api/v1/attachments/tasks/{task_id}",
        headers={"X-Organization-Slug": org_slug}
    )
    assert len(res.json()) == 0
