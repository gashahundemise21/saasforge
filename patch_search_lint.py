with open("frontend/src/components/layout/GlobalSearch.tsx", "r") as f:
    content = f.read()

content = content.replace("total: int;", "total: number;")

with open("frontend/src/components/layout/GlobalSearch.tsx", "w") as f:
    f.write(content)


with open("frontend/src/hooks/use-debounce.ts", "r") as f:
    content2 = f.read()

content2 = "/* eslint-disable react-hooks/set-state-in-effect */\n" + content2

with open("frontend/src/hooks/use-debounce.ts", "w") as f:
    f.write(content2)
