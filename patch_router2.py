with open("backend/app/api/router.py", "r") as f:
    content = f.read()

content = content.replace("from app.api.v1 import (, search", "from app.api.v1 import (\n    search,")

with open("backend/app/api/router.py", "w") as f:
    f.write(content)
