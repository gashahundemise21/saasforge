import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_organization(auth_client: AsyncClient):
    response = await auth_client.post(
        "/api/v1/organizations",
        json={"name": "Test Org"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Org"
    assert "id" in data
    assert "slug" in data


@pytest.mark.asyncio
async def test_get_my_organizations(auth_client: AsyncClient):
    # Create one
    await auth_client.post("/api/v1/organizations", json={"name": "Org 1"})

    response = await auth_client.get("/api/v1/organizations/me")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Org 1"


@pytest.mark.asyncio
async def test_get_organization_details(auth_client: AsyncClient):
    create_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Details"})
    org = create_resp.json()
    org_slug = org["slug"]

    auth_client.headers.update({"X-Organization-Slug": org_slug})

    response = await auth_client.get(f"/api/v1/organizations/{org['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Org Details"


@pytest.mark.asyncio
async def test_update_organization(auth_client: AsyncClient):
    create_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Update"})
    org = create_resp.json()
    org_slug = org["slug"]

    auth_client.headers.update({"X-Organization-Slug": org_slug})

    response = await auth_client.patch(
        f"/api/v1/organizations/{org['id']}", json={"name": "Updated Org"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Org"
