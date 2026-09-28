import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def test_login_success(async_client: AsyncClient, test_user: User) -> None:
    response = await async_client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_incorrect_password(async_client: AsyncClient, test_user: User) -> None:
    response = await async_client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"


async def test_login_incorrect_email(async_client: AsyncClient, test_user: User) -> None:
    response = await async_client.post(
        "/api/v1/login/access-token",
        data={"username": "wrong@example.com", "password": "testpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"


async def test_login_inactive_user(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    test_user.is_active = False
    db_session.add(test_user)
    await db_session.commit()

    response = await async_client.post(
        "/api/v1/login/access-token",
        data={"username": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"
