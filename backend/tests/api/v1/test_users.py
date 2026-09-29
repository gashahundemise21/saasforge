import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_current_user(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "auth@example.com"


@pytest.mark.asyncio
async def test_update_current_user(auth_client: AsyncClient):
    response = await auth_client.patch("/api/v1/users/me", json={"email": "newauth@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newauth@example.com"


@pytest.mark.asyncio
async def test_invite_user(auth_client: AsyncClient):
    # Setup: Create org
    create_resp = await auth_client.post("/api/v1/organizations", json={"name": "Org 1"})
    org = create_resp.json()
    
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})
    
    # Invite user
    invite_resp = await auth_client.post(
        f"/api/v1/organizations/{org['id']}/invites",
        json={"email": "member@example.com", "role_name": "Member"}
    )
    assert invite_resp.status_code == 201
    
    # Get members
    members_resp = await auth_client.get(f"/api/v1/organizations/{org['id']}/members")
    assert members_resp.status_code == 200
    members = members_resp.json()
    
    # Should be 2 members: the owner and the invited user
    assert len(members) == 2
    emails = [m["user"]["email"] for m in members]
    assert "member@example.com" in emails
