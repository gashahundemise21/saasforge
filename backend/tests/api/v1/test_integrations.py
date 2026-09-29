import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_integrations_crud(auth_client: AsyncClient, db_session: AsyncSession):
    # 1. Create org
    org_res = await auth_client.post(
        "/api/v1/organizations", json={"name": "Int Org"}
    )
    assert org_res.status_code == 201
    org_slug = org_res.json()["slug"]

    # 2. Create integration
    create_res = await auth_client.post(
        "/api/v1/integrations",
        json={
            "provider": "slack",
            "credentials": {"token": "xoxb-123"},
            "settings": {"channel": "#general"}
        },
        headers={"X-Organization-Slug": org_slug}
    )
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]

    # 3. Get integration
    get_res = await auth_client.get(
        f"/api/v1/integrations/{created_id}",
        headers={"X-Organization-Slug": org_slug}
    )
    assert get_res.status_code == 200
    assert get_res.json()["provider"] == "slack"

    # 4. List integrations
    list_res = await auth_client.get(
        "/api/v1/integrations",
        headers={"X-Organization-Slug": org_slug}
    )
    assert len(list_res.json()) == 1

    # 5. Delete integration
    del_res = await auth_client.delete(
        f"/api/v1/integrations/{created_id}",
        headers={"X-Organization-Slug": org_slug}
    )
    assert del_res.status_code == 204
