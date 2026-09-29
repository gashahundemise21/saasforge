import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(auth_client: AsyncClient):
    # Setup org
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Proj"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Create project
    proj_resp = await auth_client.post(
        "/api/v1/projects", json={"name": "New Project", "description": "Test Desc"}
    )
    assert proj_resp.status_code == 201
    proj = proj_resp.json()
    assert proj["name"] == "New Project"
    assert proj["organization_id"] == org["id"]


@pytest.mark.asyncio
async def test_list_projects(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Proj List"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    await auth_client.post("/api/v1/projects", json={"name": "Proj 1"})
    await auth_client.post("/api/v1/projects", json={"name": "Proj 2"})

    resp = await auth_client.get("/api/v1/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_tenant_isolation_projects(auth_client: AsyncClient):
    # Org A
    org_a_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org A"})
    org_a = org_a_resp.json()

    # Org B
    org_b_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org B"})
    org_b = org_b_resp.json()

    # Create project in Org A
    auth_client.headers.update({"X-Organization-Slug": org_a["slug"]})
    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Proj A"})
    proj_a = proj_resp.json()

    # Try to access it from Org B
    auth_client.headers.update({"X-Organization-Slug": org_b["slug"]})
    bad_get = await auth_client.get(f"/api/v1/projects/{proj_a['id']}")
    assert bad_get.status_code == 404
