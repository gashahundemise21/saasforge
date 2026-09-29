import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_api_keys_advanced(auth_client: AsyncClient, db_session: AsyncSession):
    # 1. Create org
    org_res = await auth_client.post(
        "/api/v1/organizations", json={"name": "API Org"}
    )
    assert org_res.status_code == 201
    org_slug = org_res.json()["slug"]

    # 2. Create API key with scopes
    create_res = await auth_client.post(
        "/api/v1/api-keys",
        json={"name": "Test Key", "scopes": ["projects:read", "tasks:write"]},
        headers={"X-Organization-Slug": org_slug}
    )
    assert create_res.status_code == 201
    key_id = create_res.json()["id"]
    raw_key = create_res.json()["raw_key"]
    assert "scopes" in create_res.json() # Not in response yet, wait

    # 3. Rotate key
    rotate_res = await auth_client.post(
        f"/api/v1/api-keys/{key_id}/rotate",
        headers={"X-Organization-Slug": org_slug}
    )
    assert rotate_res.status_code == 200
    new_raw_key = rotate_res.json()["raw_key"]
    assert new_raw_key != raw_key

    # 4. Get logs (should be empty but 200)
    logs_res = await auth_client.get(
        f"/api/v1/api-keys/{key_id}/logs",
        headers={"X-Organization-Slug": org_slug}
    )
    assert logs_res.status_code == 200
    assert len(logs_res.json()) == 0
