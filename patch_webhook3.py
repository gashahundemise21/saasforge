with open("backend/app/services/webhook.py", "r") as f:
    content = f.read()

# 1. Add celery import
content = content.replace("from typing import Any", "from typing import Any\nfrom app.workers.tasks import send_webhook_task")

# 2. Add raise Exception
replacement_raise = """        # Record delivery
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
            await session.commit()""", replacement_raise)

# 3. Replace background_tasks.add_task
old_dispatch = """                else:
                    background_tasks.add_task(
                        WebhookDispatcher._send_webhook,
                        endpoint_id=str(endpoint.id),
                        url=endpoint.url,
                        secret=endpoint.secret,
                        event_type=event_type,
                        payload=payload,
                    )"""

new_dispatch = """                else:
                    send_webhook_task.delay(
                        endpoint_id=str(endpoint.id),
                        url=endpoint.url,
                        secret=endpoint.secret,
                        event_type=event_type,
                        payload=payload,
                    )"""

content = content.replace(old_dispatch, new_dispatch)

with open("backend/app/services/webhook.py", "w") as f:
    f.write(content)
