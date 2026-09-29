from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInvite(BaseModel):
    email: EmailStr
    role_name: str = "Member"


class MemberResponse(BaseModel):
    user: UserResponse
    role_name: str
    joined_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
