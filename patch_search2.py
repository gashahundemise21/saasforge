with open("backend/app/services/search.py", "r") as f:
    content = f.read()

content = content.replace("or_(User.email.ilike(search_pattern), User.full_name.ilike(search_pattern))", "User.email.ilike(search_pattern)")
content = content.replace("or_(\n                    User.email.ilike(search_pattern),\n                    User.full_name.ilike(search_pattern)\n                )", "User.email.ilike(search_pattern)")
content = content.replace("title=user.full_name or user.email", "title=user.email")

with open("backend/app/services/search.py", "w") as f:
    f.write(content)
