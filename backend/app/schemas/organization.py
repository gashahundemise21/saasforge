from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None


class OrganizationResponse(OrganizationBase):
    id: str
    slug: str
    plan_id: str
    subscription_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationUserResponse(BaseModel):
    organization: OrganizationResponse
    role_name: str

    model_config = ConfigDict(from_attributes=True)
