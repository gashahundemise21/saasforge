with open("frontend/src/components/layout/GlobalSearch.tsx", "r") as f:
    content = f.read()

content = content.replace("const { currentOrganization } = useAuth();", "const { activeOrg } = useAuth();")
content = content.replace("!currentOrganization", "!activeOrg")
content = content.replace("currentOrganization.slug", "activeOrg.slug")
content = content.replace("currentOrganization", "activeOrg")

with open("frontend/src/components/layout/GlobalSearch.tsx", "w") as f:
    f.write(content)
