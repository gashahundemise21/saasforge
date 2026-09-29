with open("frontend/src/components/layout/AppSidebar.tsx", "r") as f:
    content = f.read()

import re

# Add import for GlobalSearch
if "import { GlobalSearch }" not in content:
    content = content.replace(
        "import { OrgSwitcher } from '@/components/layout/OrgSwitcher';",
        "import { OrgSwitcher } from '@/components/layout/OrgSwitcher';\nimport { GlobalSearch } from '@/components/layout/GlobalSearch';"
    )

# Add GlobalSearch below OrgSwitcher
if "<GlobalSearch />" not in content:
    content = content.replace(
        "<OrgSwitcher />\n      </SidebarHeader>",
        "<OrgSwitcher />\n        <div className=\"px-2 py-2\">\n          <GlobalSearch />\n        </div>\n      </SidebarHeader>"
    )

with open("frontend/src/components/layout/AppSidebar.tsx", "w") as f:
    f.write(content)
