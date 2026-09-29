import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_organization(auth_client: AsyncClient):
    # 1. Create org
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Search Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # 2. Create some resources
    proj_resp = await auth_client.post(
        "/api/v1/projects", json={"name": "Alpha Project", "description": "This is a great project"}
    )
    proj = proj_resp.json()

    await auth_client.post(
        f"/api/v1/projects/{proj['id']}/tasks",
        json={"title": "Important Task", "description": "Needs to be done ASAP", "status": "todo"},
    )

    # 3. Search for "Alpha"
    search_resp1 = await auth_client.get("/api/v1/search?q=Alpha")
    assert search_resp1.status_code == 200
    data1 = search_resp1.json()
    assert data1["total"] == 1
    assert data1["results"][0]["type"] == "project"
    assert data1["results"][0]["title"] == "Alpha Project"

    # 4. Search for "Important"
    search_resp2 = await auth_client.get("/api/v1/search?q=Important")
    assert search_resp2.status_code == 200
    data2 = search_resp2.json()
    assert data2["total"] == 1
    assert data2["results"][0]["type"] == "task"

    # 5. Search for user email (test user email is usually auth@example.com)
    search_resp3 = await auth_client.get("/api/v1/search?q=auth@example")
    assert search_resp3.status_code == 200
    data3 = search_resp3.json()
    assert data3["total"] >= 1
    types = [r["type"] for r in data3["results"]]
    assert "user" in types

    # 6. Search for no results
    search_resp4 = await auth_client.get("/api/v1/search?q=xyz123abc")
    assert search_resp4.status_code == 200
    assert search_resp4.json()["total"] == 0
