from enum import Enum
from pydantic import BaseModel


class RoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    viewer = "viewer"


class UserRoleOut(BaseModel):
    tenant_id: int
    role: RoleEnum

    class Config:
        orm_mode = True
