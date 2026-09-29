
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Any
from uuid import UUID

class AdminOrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    plan_id: str
    subscription_status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)



from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentSuperuser, SessionDep
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationResponse
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    session: SessionDep,
    _superuser: CurrentSuperuser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all users globally (Admin only)."""
    result = await session.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/organizations", response_model=list[AdminOrganizationResponse])
async def list_organizations(
    session: SessionDep,
    _superuser: CurrentSuperuser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all organizations globally (Admin only)."""
    result = await session.execute(select(Organization).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/users/{user_id}/suspend")
async def suspend_user(
    session: SessionDep,
    _superuser: CurrentSuperuser,
    user_id: UUID,
) -> Any:
    """Suspend or reactivate a user."""
    from app.core.exceptions import NotFoundError
    
    result = await session.execute(select(User).where(User.id == str(user_id)))
    user = result.scalars().first()
    if not user:
        raise NotFoundError("User")
        
    user.is_active = not user.is_active
    await session.commit()
    return {"status": "success", "is_active": user.is_active}
    
@router.post("/organizations/{org_id}/suspend")
async def suspend_organization(
    session: SessionDep,
    _superuser: CurrentSuperuser,
    org_id: UUID,
) -> Any:
    """Toggle organization suspension (we can use deleted_at or a new is_active flag). For now we'll set deleted_at."""
    from app.core.exceptions import NotFoundError
    from app.db.base import get_utc_now
    
    result = await session.execute(select(Organization).where(Organization.id == str(org_id)))
    org = result.scalars().first()
    if not org:
        raise NotFoundError("Organization")
        
    if org.deleted_at:
        org.deleted_at = None
    else:
        org.deleted_at = get_utc_now()
        
    await session.commit()
    return {"status": "success", "is_suspended": org.deleted_at is not None}
