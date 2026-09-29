from fastapi import APIRouter

from app.api.v1 import auth, health, organizations, users, projects, tasks, api_keys, audit_logs, webhooks

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(auth.router, tags=["auth"])
router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(projects.router, prefix="/projects", tags=["projects"])
router.include_router(tasks.router, tags=["tasks"])
router.include_router(api_keys.router, prefix="/api-keys", tags=["api_keys"])
router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit_logs"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
