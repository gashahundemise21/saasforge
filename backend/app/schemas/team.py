from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserResponse


class TeamBase(BaseModel):
    name: str
    description: str | None = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class TeamResponse(TeamBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamMemberResponse(BaseModel):
    id: str
    team_id: str
    user_id: str
    role: str
    created_at: datetime
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class TeamInvitationCreate(BaseModel):
    email: str
    role: str = "member"


class TeamInvitationResponse(BaseModel):
    id: str
    team_id: str
    email: str
    role: str
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
