from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: CurrentUser) -> UserResponse:
    """Get current user."""
    return current_user  # type: ignore


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    session: SessionDep, current_user: CurrentUser, user_in: UserUpdate
) -> UserResponse:
    """Update current user."""
    return await UserService.update_user(session, current_user, user_in)  # type: ignore
