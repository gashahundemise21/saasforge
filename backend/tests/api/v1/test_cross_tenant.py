import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import get_password_hash, create_access_token

@pytest.fixture
async def user_a(db_session: AsyncSession) -> User:
    user = User(
        email="usera@example.com",
        hashed_password=get_password_hash("password"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def user_b(db_session: AsyncSession) -> User:
    user = User(
        email="userb@example.com",
        hashed_password=get_password_hash("password"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def client_a(async_client: AsyncClient, user_a: User) -> AsyncClient:
    token = create_access_token(user_a.id)
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.fixture
async def client_b(async_client: AsyncClient, user_b: User) -> AsyncClient:
    token = create_access_token(user_b.id)
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.mark.asyncio
async def test_cross_tenant_isolation(client_a: AsyncClient, client_b: AsyncClient) -> None:
    # 1. User A creates Org A
    res = await client_a.post("/api/v1/organizations", json={"name": "Org A"})
    assert res.status_code == 201
    org_a_slug = res.json()["slug"]

    # 2. User B creates Org B
    res = await client_b.post("/api/v1/organizations", json={"name": "Org B"})
    assert res.status_code == 201
    org_b_slug = res.json()["slug"]

    # 3. User A creates Project A in Org A
    res = await client_a.post("/api/v1/projects", headers={"X-Organization-Slug": org_a_slug}, json={
        "name": "Project A",
        "description": "Project for A"
    })
    assert res.status_code == 201
    project_a_id = res.json()["id"]

    # 4. User A creates Task A in Project A
    res = await client_a.post(f"/api/v1/projects/{project_a_id}/tasks", headers={"X-Organization-Slug": org_a_slug}, json={
        "title": "Task A",
        "status": "todo",
        "priority": "medium"
    })
    assert res.status_code == 201
    task_a_id = res.json()["id"]
    
    # 5. User A creates API Key in Org A
    res = await client_a.post("/api/v1/api-keys", headers={"X-Organization-Slug": org_a_slug}, json={
        "name": "API Key A",
        "expires_in_days": 30
    })
    assert res.status_code == 201
    
    # 6. User A creates Team A in Org A
    res = await client_a.post("/api/v1/teams", headers={"X-Organization-Slug": org_a_slug}, json={
        "name": "Team A"
    })
    assert res.status_code == 201
    team_a_id = res.json()["id"]

    # Now verify User B cannot access Org A's resources

    # User B tries to read Org A
    res = await client_b.get("/api/v1/organizations/me")
    assert org_a_slug not in [org["slug"] for org in res.json()]
    
    # User B tries to read Project A
    res = await client_b.get(f"/api/v1/projects/{project_a_id}", headers={"X-Organization-Slug": org_a_slug})
    assert res.status_code in (403, 404, 400)
    
    # User B tries to read Project A using Org B header (cross-tenant)
    res = await client_b.get(f"/api/v1/projects/{project_a_id}", headers={"X-Organization-Slug": org_b_slug})
    assert res.status_code == 404

    # User B tries to read Task A
    res = await client_b.get(f"/api/v1/tasks/{task_a_id}", headers={"X-Organization-Slug": org_b_slug})
    assert res.status_code == 404
    
    # User B tries to list API keys of Org A
    res = await client_b.get("/api/v1/api-keys", headers={"X-Organization-Slug": org_a_slug})
    assert res.status_code in (403, 404, 400)

    # User B tries to read Team A
    res = await client_b.get(f"/api/v1/teams/{team_a_id}", headers={"X-Organization-Slug": org_b_slug})
    assert res.status_code == 404
    
    # User B tries to delete Project A
    res = await client_b.delete(f"/api/v1/projects/{project_a_id}", headers={"X-Organization-Slug": org_b_slug})
    assert res.status_code == 404

    # User B tries to modify Task A
    res = await client_b.patch(f"/api/v1/tasks/{task_a_id}", headers={"X-Organization-Slug": org_b_slug}, json={"status": "done"})
    assert res.status_code == 404
    
    # Ensure client cleanup
    await client_a.aclose()
    await client_b.aclose()
