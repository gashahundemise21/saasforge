import hmac
import json
import secrets
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import AsyncSessionLocal
from app.models.webhook import WebhookDelivery, WebhookEndpoint
from app.schemas.webhook import WebhookEndpointCreate


class WebhookEndpointService:
    @staticmethod
    async def create_endpoint(
        session: AsyncSession, org_id: str | UUID, endpoint_in: WebhookEndpointCreate
    ) -> WebhookEndpoint:
        # Generate a secure signing secret
        secret = f"whsec_{secrets.token_urlsafe(32)}"

        endpoint = WebhookEndpoint(
            organization_id=str(org_id),
            url=str(endpoint_in.url),
            events=endpoint_in.events,
            secret=secret,
        )
        session.add(endpoint)
        await session.commit()
        await session.refresh(endpoint)
        return endpoint

    @staticmethod
    async def get_org_endpoints(
        session: AsyncSession, org_id: str | UUID
    ) -> list[WebhookEndpoint]:
        result = await session.execute(
            select(WebhookEndpoint).where(WebhookEndpoint.organization_id == str(org_id))
        )
        return list(result.scalars().all())

    @staticmethod
    async def delete_endpoint(
        session: AsyncSession, org_id: str | UUID, endpoint_id: UUID
    ) -> None:
        result = await session.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.id == str(endpoint_id),
                WebhookEndpoint.organization_id == str(org_id),
            )
        )
        endpoint = result.scalars().first()
        if not endpoint:
            raise NotFoundError("WebhookEndpoint")

        await session.delete(endpoint)
        await session.commit()

    @staticmethod
    async def list_deliveries(
        session: AsyncSession, org_id: str | UUID, endpoint_id: UUID
    ) -> list[WebhookDelivery]:
        # Validate endpoint ownership
        result = await session.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.id == str(endpoint_id),
                WebhookEndpoint.organization_id == str(org_id),
            )
        )
        if not result.scalars().first():
            raise NotFoundError("WebhookEndpoint")

        # Fetch deliveries
        deliveries = await session.execute(
            select(WebhookDelivery)
            .where(WebhookDelivery.endpoint_id == str(endpoint_id))
            .order_by(desc(WebhookDelivery.created_at))
            .limit(100)
        )
        return list(deliveries.scalars().all())


class WebhookDispatcher:
    @staticmethod
    def _generate_signature(secret: str, payload_bytes: bytes) -> str:
        """Generate HMAC-SHA256 signature."""
        return hmac.new(secret.encode("utf-8"), payload_bytes, digestmod="sha256").hexdigest()

    @staticmethod
    async def _send_webhook(
        endpoint_id: str,
        url: str,
        secret: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """
        Actually perform the HTTP request. Designed to run in a BackgroundTask.
        Spawns its own session to record the delivery result.
        """
        payload_bytes = json.dumps(payload).encode("utf-8")
        signature = WebhookDispatcher._generate_signature(secret, payload_bytes)

        headers = {
            "Content-Type": "application/json",
            "X-SaaSForge-Event": event_type,
            "X-SaaSForge-Signature": signature,
        }

        success = False
        status_code = None
        error_message = None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, content=payload_bytes, headers=headers)
                status_code = response.status_code
                if 200 <= status_code < 300:
                    success = True
                else:
                    error_message = f"Received status {status_code}"
        except httpx.RequestError as e:
            error_message = f"Request failed: {str(e)}"
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"

        # Record delivery
        async with AsyncSessionLocal() as session:
            delivery = WebhookDelivery(
                endpoint_id=endpoint_id,
                event_type=event_type,
                payload=payload,
                status_code=status_code,
                success=success,
                error_message=error_message,
            )
            session.add(delivery)
            await session.commit()

    @staticmethod
    async def dispatch_event(
        session: AsyncSession,
        background_tasks: Any,
        org_id: str | UUID,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """
        Queue webhook delivery for any matching active endpoints.
        """
        from app.core.config import settings

        result = await session.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.organization_id == str(org_id),
                WebhookEndpoint.is_active == True,
            )
        )
        endpoints = result.scalars().all()

        for endpoint in endpoints:
            matches = False
            for sub in endpoint.events:
                if sub == "*" or sub == event_type:
                    matches = True
                    break
                if sub.endswith(".*") and event_type.startswith(sub[:-2]):
                    matches = True
                    break

            if matches:
                if settings.ENVIRONMENT == "test":
                    # Run synchronously in tests using the current session to avoid transaction issues
                    await WebhookDispatcher._send_webhook_sync_test(
                        session=session,
                        endpoint_id=str(endpoint.id),
                        url=endpoint.url,
                        secret=endpoint.secret,
                        event_type=event_type,
                        payload=payload,
                    )
                else:
                    background_tasks.add_task(
                        WebhookDispatcher._send_webhook,
                        endpoint_id=str(endpoint.id),
                        url=endpoint.url,
                        secret=endpoint.secret,
                        event_type=event_type,
                        payload=payload,
                    )

    @staticmethod
    async def _send_webhook_sync_test(
        session: AsyncSession,
        endpoint_id: str,
        url: str,
        secret: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """Synchronous version for testing to avoid connection issues."""
        payload_bytes = json.dumps(payload).encode("utf-8")
        signature = WebhookDispatcher._generate_signature(secret, payload_bytes)
        headers = {
            "Content-Type": "application/json",
            "X-SaaSForge-Event": event_type,
            "X-SaaSForge-Signature": signature,
        }

        success = False
        status_code = None
        error_message = None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, content=payload_bytes, headers=headers)
                status_code = response.status_code
                if 200 <= status_code < 300:
                    success = True
                else:
                    error_message = f"Received status {status_code}"
        except httpx.RequestError as e:
            error_message = f"Request failed: {str(e)}"

        delivery = WebhookDelivery(
            endpoint_id=endpoint_id,
            event_type=event_type,
            payload=payload,
            status_code=status_code,
            success=success,
            error_message=error_message,
        )
        session.add(delivery)
        # Flush to make it visible to tests, commit will happen in caller
        await session.flush()
