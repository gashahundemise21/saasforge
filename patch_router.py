with open("backend/app/api/router.py", "r") as f:
    content = f.read()

import re
# 1. Update imports
content = re.sub(
    r'(from app\.api\.v1 import.*)',
    r'\1, search',
    content
)

# 2. Add router
content += """
router.include_router(search.router, prefix="/search", tags=["search"])
"""

with open("backend/app/api/router.py", "w") as f:
    f.write(content)
