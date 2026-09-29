from fastapi import APIRouter

from app.api.v1 import auth, health, organizations, users, projects, tasks

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(auth.router, tags=["auth"])
router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(projects.router, prefix="/projects", tags=["projects"])
router.include_router(tasks.router, tags=["tasks"])
