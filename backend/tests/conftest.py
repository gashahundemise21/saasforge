from collections.abc import AsyncGenerator

import pytest
import os
os.environ["ENVIRONMENT"] = "test"

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.session import engine
from app.main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.
    """
    async with engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        
        async_session = AsyncSession(conn, expire_on_commit=False)
        
        @pytest.hookimpl
        def pytest_exception_interact() -> None:
            pass
            
        yield async_session
        
        await async_session.close()
        await conn.rollback()


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> "User":
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="auth@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_client(async_client: AsyncClient, test_user: "User") -> AsyncClient:
    from app.core.security import create_access_token
    
    token = create_access_token(test_user.id)
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    return async_client
