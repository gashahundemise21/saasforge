import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.organization import Organization


@pytest.mark.asyncio
async def test_project_quota_enforcement(auth_client: AsyncClient, db_session: AsyncSession):
    # Setup Org
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Quota Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Org is "free" by default, limit is 2 projects
    # Create 1st
    resp1 = await auth_client.post("/api/v1/projects", json={"name": "Project 1", "description": ""})
    assert resp1.status_code == 201

    # Create 2nd
    resp2 = await auth_client.post("/api/v1/projects", json={"name": "Project 2", "description": ""})
    assert resp2.status_code == 201

    # Create 3rd -> Should fail
    resp3 = await auth_client.post("/api/v1/projects", json={"name": "Project 3", "description": ""})
    assert resp3.status_code == 402
    assert resp3.json()["error"]["code"] == "PROJECT_QUOTA_EXCEEDED"

    # Upgrade to Pro
    org_db = (await db_session.execute(select(Organization).where(Organization.id == org["id"]))).scalar_one()
    org_db.plan_id = "price_pro"
    await db_session.commit()

    # Create 3rd -> Should succeed now
    resp4 = await auth_client.post("/api/v1/projects", json={"name": "Project 3", "description": ""})
    assert resp4.status_code == 201


@pytest.mark.asyncio
async def test_member_quota_enforcement(auth_client: AsyncClient, db_session: AsyncSession):
    # Setup Org
    org_resp = await auth_client.post("/api/v1/organizations", json={"name": "Member Quota Org"})
    org = org_resp.json()
    auth_client.headers.update({"X-Organization-Slug": org["slug"]})

    # Limit is 3 members. The creator is 1 member.
    # So we can invite 2 more.
    resp1 = await auth_client.post("/api/v1/organizations/" + org["id"] + "/invites", json={"email": "u1@test.com", "role_name": "Member"})
    assert resp1.status_code == 201

    resp2 = await auth_client.post("/api/v1/organizations/" + org["id"] + "/invites", json={"email": "u2@test.com", "role_name": "Member"})
    assert resp2.status_code == 201

    # 4th member should fail
    resp3 = await auth_client.post("/api/v1/organizations/" + org["id"] + "/invites", json={"email": "u3@test.com", "role_name": "Member"})
    assert resp3.status_code == 402
    assert resp3.json()["error"]["code"] == "MEMBER_QUOTA_EXCEEDED"
