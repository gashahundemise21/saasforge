with open("backend/tests/api/v1/test_search.py", "r") as f:
    content = f.read()

content = content.replace("test@example", "auth@example")

with open("backend/tests/api/v1/test_search.py", "w") as f:
    f.write(content)
