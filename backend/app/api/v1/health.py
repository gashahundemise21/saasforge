from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    message: str


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "SaaSForge API is healthy."}


@router.get("/health/live", response_model=HealthResponse)
async def liveness_check() -> dict[str, str]:
    return {"status": "ok", "message": "Service is live."}


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check() -> dict[str, str]:
    # In the future, check database and redis connections here
    return {"status": "ok", "message": "Service is ready."}
