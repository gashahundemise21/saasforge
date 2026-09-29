import re

with open("backend/app/services/webhook.py", "r") as f:
    content = f.read()

replacement = """        # Record delivery
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
            
        if not success:
            raise Exception(f"Webhook delivery failed: {error_message}")"""

content = content.replace("""        # Record delivery
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
            await session.commit()""", replacement)

# Change dispatch_event to use Celery
celery_import = "from app.workers.tasks import send_webhook_task"
if celery_import not in content:
    content = content.replace("from typing import Any", "from typing import Any\n" + celery_import)

celery_dispatch = """                if settings.ENVIRONMENT == "test":
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
                    send_webhook_task.delay(
                        endpoint_id=str(endpoint.id),
                        url=endpoint.url,
                        secret=endpoint.secret,
                        event_type=event_type,
                        payload=payload,
                    )"""

content = re.sub(
    r'                if settings.ENVIRONMENT == "test":\s*# Run synchronously in tests.*?else:\s*background_tasks.add_task\([^)]+\)',
    celery_dispatch,
    content,
    flags=re.DOTALL
)

with open("backend/app/services/webhook.py", "w") as f:
    f.write(content)
