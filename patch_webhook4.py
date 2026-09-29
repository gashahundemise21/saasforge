with open("backend/app/services/webhook.py", "r") as f:
    content = f.read()

import re
content = re.sub(r'else:\s*send_webhook_task\.delay\(', 'else:\n                    from app.workers.tasks import send_webhook_task\n                    send_webhook_task.delay(', content)

with open("backend/app/services/webhook.py", "w") as f:
    f.write(content)
