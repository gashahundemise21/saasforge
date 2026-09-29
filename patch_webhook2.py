with open("backend/app/services/webhook.py", "r") as f:
    content = f.read()

import re
content = re.sub(r'send_webhook_task\.delay\([^)]+\),\s*url=endpoint\.url,\s*secret=endpoint\.secret,\s*event_type=event_type,\s*payload=payload,\s*\)', 'send_webhook_task.delay(\n                        endpoint_id=str(endpoint.id),\n                        url=endpoint.url,\n                        secret=endpoint.secret,\n                        event_type=event_type,\n                        payload=payload,\n                    )', content)

with open("backend/app/services/webhook.py", "w") as f:
    f.write(content)
