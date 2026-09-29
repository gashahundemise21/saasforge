from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.integration import IntegrationConnection
from app.schemas.integration import IntegrationConnectionCreate, IntegrationConnectionUpdate


class IntegrationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_connection(
        self, organization_id: str, obj_in: IntegrationConnectionCreate
    ) -> IntegrationConnection:
        # Check if already exists for this provider
        stmt = select(IntegrationConnection).where(
            IntegrationConnection.organization_id == organization_id,
            IntegrationConnection.provider == obj_in.provider
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Integration {obj_in.provider} already exists for this organization"
            )

        db_obj = IntegrationConnection(
            organization_id=organization_id,
            **obj_in.model_dump()
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_connections(self, organization_id: str) -> list[IntegrationConnection]:
        stmt = select(IntegrationConnection).where(
            IntegrationConnection.organization_id == organization_id
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_connection(self, organization_id: str, connection_id: str) -> Optional[IntegrationConnection]:
        stmt = select(IntegrationConnection).where(
            IntegrationConnection.organization_id == organization_id,
            IntegrationConnection.id == connection_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_connection(
        self, organization_id: str, connection_id: str, obj_in: IntegrationConnectionUpdate
    ) -> IntegrationConnection:
        db_obj = await self.get_connection(organization_id, connection_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration connection not found"
            )

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete_connection(self, organization_id: str, connection_id: str) -> None:
        db_obj = await self.get_connection(organization_id, connection_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration connection not found"
            )

        await self.db.delete(db_obj)
        await self.db.commit()

