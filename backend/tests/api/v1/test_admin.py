import pytest
from httpx import AsyncClient
from app.models.user import User

@pytest.fixture
def override_superuser():
    from app.api.deps import get_current_superuser
    from app.main import app
    from app.models.user import User
    
    async def mock_super():
        u = User(id="super", email="s@s.com", is_superuser=True)
        return u
        
    app.dependency_overrides[get_current_superuser] = mock_super
    yield
    app.dependency_overrides.pop(get_current_superuser)

@pytest.mark.asyncio
async def test_admin_list_users(auth_client: AsyncClient, override_superuser):
    res = await auth_client.get("/api/v1/admin/users")
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_admin_forbidden_for_normal_user(auth_client: AsyncClient, test_user: User):
    res = await auth_client.get("/api/v1/admin/users")
    assert res.status_code == 403
