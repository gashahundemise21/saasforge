from typing import Any

# Define hard limits for resources per plan
# -1 indicates unlimited.
PLAN_QUOTAS: dict[str, dict[str, int]] = {
    "free": {
        "max_projects": 2,
        "max_members": 3,
    },
    "price_pro": {  # Example stripe price id
        "max_projects": 10,
        "max_members": 10,
    },
    "price_premium": {
        "max_projects": -1,
        "max_members": -1,
    },
}

def get_quota(plan_id: str, resource: str) -> int:
    """Retrieve the quota limit for a given plan and resource."""
    # Fallback to free limits if plan is unknown
    plan_limits = PLAN_QUOTAS.get(plan_id, PLAN_QUOTAS["free"])
    return plan_limits.get(resource, 0)
