import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_liveness_check(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/health/live")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_readiness_check(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/health/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
