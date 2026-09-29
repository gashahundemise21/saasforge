from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.organization import Organization
from app.models.user import OrganizationUser, User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token", auto_error=False
)

TokenDep = Annotated[str | None, Depends(oauth2_scheme)]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user_optional(session: SessionDep, token: TokenDep) -> User | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            return None
    except (JWTError, ValidationError):
        return None

    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        return None

    return user


async def get_current_user(user: User | None = Depends(get_current_user_optional)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_organization(
    request: Request, session: SessionDep, user: User | None = Depends(get_current_user_optional)
) -> Organization:
    # 1. Try API Key Auth
    api_key_header = request.headers.get("X-API-Key")
    if api_key_header:
        from app.models.api_key import ApiKey

        # We need to find the api key.
        # A simple approach is finding by raw_key hash.
        # In production we might look up by prefix first to avoid hashing if invalid.
        # For simplicity, we just fetch all keys by prefix, then verify hash.
        prefix = (
            api_key_header.split("_")[0] + "_" + api_key_header.split("_")[1]
            if len(api_key_header.split("_")) > 1
            else ""
        )

        stmt = (
            select(ApiKey)
            .options(selectinload(ApiKey.organization))
            .where(
                ApiKey.prefix == prefix,
                ApiKey.is_active == True,
                ApiKey.organization.has(Organization.deleted_at.is_(None)),
            )
        )
        result = await session.execute(stmt)
        api_keys = result.scalars().all()

        from app.core.security import verify_password

        valid_key = next(
            (k for k in api_keys if verify_password(api_key_header, k.hashed_key)), None
        )

        if valid_key:
            from app.db.base import get_utc_now
            now = get_utc_now()
            if valid_key.expires_at and valid_key.expires_at < now:
                raise HTTPException(status_code=401, detail="API Key has expired")

            valid_key.last_used_at = now
            await session.commit()
            request.state.api_key = valid_key
            request.state.organization_user = None  # No user context
            return valid_key.organization

    # 2. Try User JWT Auth
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    org_slug = request.headers.get("X-Organization-Slug")
    if not org_slug:
        raise HTTPException(status_code=400, detail="X-Organization-Slug header missing")

    stmt = (
        select(OrganizationUser)
        .options(selectinload(OrganizationUser.organization), selectinload(OrganizationUser.role))
        .join(Organization)
        .where(
            OrganizationUser.user_id == user.id,
            Organization.slug == org_slug,
            Organization.deleted_at.is_(None),
        )
    )
    result = await session.execute(stmt)
    org_user = result.scalar_one_or_none()

    if not org_user:
        raise HTTPException(status_code=403, detail="Not enough permissions in this organization")

    request.state.organization_user = org_user
    request.state.api_key = None
    return org_user.organization


CurrentOrganization = Annotated[Organization, Depends(get_current_organization)]


class ActorContext(BaseModel):
    actor_id: str
    actor_type: str
    ip_address: str | None


def get_current_actor(request: Request) -> ActorContext:
    ip_address = request.client.host if request.client else None

    # Check if API key is set
    api_key = getattr(request.state, "api_key", None)
    if api_key:
        return ActorContext(actor_id=str(api_key.id), actor_type="api_key", ip_address=ip_address)

    # Check if user is set
    org_user = getattr(request.state, "organization_user", None)
    if org_user:
        return ActorContext(
            actor_id=str(org_user.user_id), actor_type="user", ip_address=ip_address
        )

    # Fallback to current_user if outside org context
    user = getattr(request.state, "user", None)
    if user:
        return ActorContext(actor_id=str(user.id), actor_type="user", ip_address=ip_address)

    return ActorContext(actor_id="system", actor_type="system", ip_address=ip_address)


CurrentActor = Annotated[ActorContext, Depends(get_current_actor)]


class RequireRole:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request, current_org: CurrentOrganization):
        # If authenticated via API Key, we bypass user role checks.
        # Alternatively, we could bind roles to API keys, but for now we grant full access.
        if getattr(request.state, "api_key", None):
            return None

        org_user: OrganizationUser = request.state.organization_user
        if org_user.user.is_superuser:
            return org_user

        if not org_user.role or org_user.role.name not in self.allowed_roles:
            raise HTTPException(
                status_code=403, detail="User role does not have required permissions"
            )

        return org_user


class RequireScope:
    def __init__(self, allowed_scopes: list[str]) -> None:
        self.allowed_scopes = allowed_scopes

    def __call__(self, request: Request, current_org: CurrentOrganization):
        api_key = getattr(request.state, "api_key", None)
        if api_key:
            # Check scopes
            key_scopes = set(api_key.scopes)
            # If empty scopes, maybe full access or no access. Let's say full access for backward compatibility,
            # or if 'all' is in scopes.
            if not key_scopes:
                return None
            
            has_scope = any(scope in key_scopes for scope in self.allowed_scopes)
            if not has_scope:
                raise HTTPException(status_code=403, detail="API Key does not have required scope")
            return None
            
        # If user, rely on RequireRole. Or just pass.
        return None


async def get_current_superuser(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return user

CurrentSuperuser = Annotated[User, Depends(get_current_superuser)]
