from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from app.api.deps import SessionDep
import redis.asyncio as redis
from app.core.config import settings

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
async def readiness_check(session: SessionDep) -> dict[str, str]:
    # Check Database
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e}"
        )
    
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis connection failed: {e}"
        )
        
    return {"status": "ok", "message": "Service is ready."}
