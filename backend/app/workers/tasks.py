import asyncio
from typing import Any

from app.services.webhook import WebhookDispatcher
from app.worker import celery_app


@celery_app.task(name="send_webhook_task", bind=True, max_retries=3, default_retry_delay=60)
def send_webhook_task(
    self, endpoint_id: str, url: str, secret: str, event_type: str, payload: dict[str, Any]
):
    try:
        # We need to run the async function in a synchronous context
        asyncio.run(
            WebhookDispatcher._send_webhook(
                endpoint_id=endpoint_id,
                url=url,
                secret=secret,
                event_type=event_type,
                payload=payload,
            )
        )
    except Exception as exc:
        # Retry for any exception
        self.retry(exc=exc)
