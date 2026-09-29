import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_team(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Team 1"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    response = await auth_client.post(
        "/api/v1/teams",
        json={"name": "Engineering", "description": "The engineering team"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Engineering"
    assert data["description"] == "The engineering team"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_teams(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Team 2"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    await auth_client.post(
        "/api/v1/teams",
        json={"name": "Sales"},
    )

    response = await auth_client.get("/api/v1/teams")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Sales"

@pytest.mark.asyncio
async def test_invite_member(auth_client: AsyncClient):
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org Team 3"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    res = await auth_client.post(
        "/api/v1/teams",
        json={"name": "Support"},
    )
    team_id = res.json()["id"]

    res_fail = await auth_client.post(
        f"/api/v1/teams/{team_id}/invitations",
        json={"email": "newuser@example.com"},
    )
    assert res_fail.status_code == 400

    res_org_invite = await auth_client.post(
        f"/api/v1/organizations/{org['id']}/invites",
        json={"email": "newuser@example.com", "role_name": "Member"}
    )
    assert res_org_invite.status_code == 201

    res_success = await auth_client.post(
        f"/api/v1/teams/{team_id}/invitations",
        json={"email": "newuser@example.com"},
    )
    assert res_success.status_code == 201
    assert res_success.json()["status"] == "pending"

@pytest.mark.asyncio
async def test_tenant_isolation_teams(auth_client: AsyncClient):
    # Org A
    org_a_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org A"})
    org_a = org_a_resp.json()
    
    # Org B
    org_b_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org B"})
    org_b = org_b_resp.json()
    
    # Create team in Org A
    auth_client.headers.update({"X-Organization-Slug": org_a["slug"]})
    team_resp = await auth_client.post("/api/v1/teams", json={"name": "Team A"})
    team_a = team_resp.json()
    
    # Try to access it from Org B
    auth_client.headers.update({"X-Organization-Slug": org_b["slug"]})
    bad_get = await auth_client.get(f"/api/v1/teams/{team_a['id']}")
    assert bad_get.status_code == 404
