import re

with open("backend/app/api/v1/search.py", "r") as f:
    content = f.read()

content = content.replace('@router.get("/",', '@router.get("",')

with open("backend/app/api/v1/search.py", "w") as f:
    f.write(content)
