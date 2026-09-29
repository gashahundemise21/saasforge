from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_api_key
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate


class ApiKeyService:
    @staticmethod
    async def create_api_key(
        session: AsyncSession, org_id: str | UUID, api_key_in: ApiKeyCreate
    ) -> tuple[ApiKey, str]:
        """Create a new API key for the organization and return (ApiKey, raw_secret)."""
        prefix, raw_key, hashed_key = generate_api_key()
        
        api_key = ApiKey(
            organization_id=str(org_id),
            name=api_key_in.name,
            prefix=prefix,
            hashed_key=hashed_key,
            expires_at=api_key_in.expires_at,
        )
        session.add(api_key)
        await session.commit()
        await session.refresh(api_key)
        
        return api_key, raw_key

    @staticmethod
    async def list_api_keys(session: AsyncSession, org_id: str | UUID) -> list[ApiKey]:
        """Get all active API keys for an organization."""
        result = await session.execute(
            select(ApiKey)
            .where(ApiKey.organization_id == str(org_id))
            .where(ApiKey.is_active == True)
        )
        return list(result.scalars().all())

    @staticmethod
    async def revoke_api_key(session: AsyncSession, org_id: str | UUID, key_id: str | UUID) -> None:
        """Revoke (soft delete) an API key."""
        result = await session.execute(
            select(ApiKey)
            .where(ApiKey.id == str(key_id))
            .where(ApiKey.organization_id == str(org_id))
            .where(ApiKey.is_active == True)
        )
        api_key = result.scalars().first()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API Key not found or already revoked",
            )
            
        api_key.is_active = False
        await session.commit()
