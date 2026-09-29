import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_api_key(auth_client: AsyncClient):
    # Setup org
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "API Key Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Create API key
    key_resp = await auth_client.post("/api/v1/api-keys", json={"name": "Prod Key"})
    assert key_resp.status_code == 201
    key_data = key_resp.json()

    assert key_data["name"] == "Prod Key"
    assert "raw_key" in key_data
    assert key_data["raw_key"].startswith("sk_live_")


@pytest.mark.asyncio
async def test_list_and_revoke_api_keys(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "API Key Org 2"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    key1 = (await auth_client.post("/api/v1/api-keys", json={"name": "Key 1"})).json()
    key2 = (await auth_client.post("/api/v1/api-keys", json={"name": "Key 2"})).json()

    # List keys
    list_resp = await auth_client.get("/api/v1/api-keys")
    assert list_resp.status_code == 200
    keys = list_resp.json()
    assert len(keys) == 2

    # Revoke key 1
    revoke_resp = await auth_client.delete(f"/api/v1/api-keys/{key1['id']}")
    assert revoke_resp.status_code == 204

    # List again
    list_resp = await auth_client.get("/api/v1/api-keys")
    keys = list_resp.json()
    assert len(keys) == 1
    assert keys[0]["id"] == key2["id"]


@pytest.mark.asyncio
async def test_access_via_api_key(auth_client: AsyncClient, async_client: AsyncClient):
    # Setup org and key using user auth
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "API Access Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    key_resp = await auth_client.post("/api/v1/api-keys", json={"name": "Access Key"})
    key_data = key_resp.json()
    raw_key = key_data["raw_key"]

    # Use standard client without JWT, but with X-API-Key
    async_client.headers.update({"X-API-Key": raw_key})

    # Test programmatic access: Create a project
    proj_resp = await async_client.post("/api/v1/projects", json={"name": "API Created Project"})
    assert proj_resp.status_code == 201

    # List projects
    list_resp = await async_client.get("/api/v1/projects")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
