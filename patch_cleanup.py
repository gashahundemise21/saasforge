import re
import glob

# 1. Patch webhook.py
with open("backend/app/services/webhook.py", "r") as f:
    content = f.read()

content = content.replace("background_tasks: Any,", "")
with open("backend/app/services/webhook.py", "w") as f:
    f.write(content)

# 2. Patch API routes
for filename in glob.glob("backend/app/api/v1/*.py"):
    with open(filename, "r") as f:
        content = f.read()
    
    # Remove background_tasks dependency in route definitions
    content = re.sub(r'\s*background_tasks:\s*BackgroundTasks,', '', content)
    
    # Remove it from imports if not used elsewhere
    # Wait, we might need BackgroundTasks if we don't remove it from import.
    # It's safer to just replace 'BackgroundTasks, ' with '' and so on.
    content = content.replace("BackgroundTasks, ", "")
    content = content.replace("from fastapi import APIRouter, BackgroundTasks, Depends", "from fastapi import APIRouter, Depends")
    
    # Remove the argument in the dispatch_event call
    content = re.sub(r'\s*background_tasks=background_tasks,', '', content)
    
    with open(filename, "w") as f:
        f.write(content)
