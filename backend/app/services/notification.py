from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationService:
    @staticmethod
    async def create_notification(
        session: AsyncSession,
        user_id: str | UUID,
        organization_id: str | UUID,
        title: str,
        message: str,
        type: str,
        action_url: str | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=str(user_id),
            organization_id=str(organization_id),
            title=title,
            message=message,
            type=type,
            action_url=action_url,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    @staticmethod
    async def list_user_notifications(
        session: AsyncSession,
        user_id: str | UUID,
        organization_id: str | UUID,
        limit: int = 50,
        skip: int = 0,
    ) -> list[Notification]:
        result = await session.execute(
            select(Notification)
            .where(
                Notification.user_id == str(user_id),
                Notification.organization_id == str(organization_id),
            )
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_unread_count(
        session: AsyncSession,
        user_id: str | UUID,
        organization_id: str | UUID,
    ) -> int:
        from sqlalchemy import func

        result = await session.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == str(user_id),
                Notification.organization_id == str(organization_id),
                Notification.read_at.is_(None),
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def mark_as_read(
        session: AsyncSession,
        notification_id: str | UUID,
        user_id: str | UUID,
        organization_id: str | UUID,
    ) -> Notification | None:
        result = await session.execute(
            select(Notification).where(
                Notification.id == str(notification_id),
                Notification.user_id == str(user_id),
                Notification.organization_id == str(organization_id),
            )
        )
        notification = result.scalar_one_or_none()

        if notification and not notification.read_at:
            notification.read_at = datetime.now(UTC)
            await session.commit()
            await session.refresh(notification)

        return notification

    @staticmethod
    async def mark_all_as_read(
        session: AsyncSession,
        user_id: str | UUID,
        organization_id: str | UUID,
    ) -> None:
        await session.execute(
            update(Notification)
            .where(
                Notification.user_id == str(user_id),
                Notification.organization_id == str(organization_id),
                Notification.read_at.is_(None),
            )
            .values(read_at=datetime.now(UTC))
        )
        await session.commit()
