from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.organization import Organization
from app.models.user import OrganizationUser, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_organization(
    request: Request, session: SessionDep, current_user: CurrentUser
) -> Organization:
    org_slug = request.headers.get("X-Organization-Slug")
    if not org_slug:
        raise HTTPException(status_code=400, detail="X-Organization-Slug header missing")
        
    # Verify organization exists and user is a member
    stmt = (
        select(OrganizationUser)
        .options(selectinload(OrganizationUser.organization), selectinload(OrganizationUser.role))
        .join(Organization)
        .where(
            OrganizationUser.user_id == current_user.id,
            Organization.slug == org_slug,
            Organization.deleted_at.is_(None)
        )
    )
    result = await session.execute(stmt)
    org_user = result.scalar_one_or_none()
    
    if not org_user:
        raise HTTPException(status_code=403, detail="Not enough permissions in this organization")
        
    request.state.organization_user = org_user
    return org_user.organization


CurrentOrganization = Annotated[Organization, Depends(get_current_organization)]


class RequireRole:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self, request: Request, current_user: CurrentUser, current_org: CurrentOrganization
    ) -> OrganizationUser:
        if current_user.is_superuser:
            return request.state.organization_user
            
        org_user: OrganizationUser = request.state.organization_user
        if not org_user.role or org_user.role.name not in self.allowed_roles:
            raise HTTPException(
                status_code=403, detail="User role does not have required permissions"
            )
            
        return org_user
