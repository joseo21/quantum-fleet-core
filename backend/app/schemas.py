from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Any, Dict, Optional

class TenantCreate(BaseModel):
    name: str
    slug: str

class TenantOut(BaseModel):
    id: int; name: str; slug: str
    class Config: from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "admin"
    tenant_id: int

class UserOut(BaseModel):
    id: int; email: EmailStr; role: str; tenant_id: int
    class Config: from_attributes = True

class DeviceCreate(BaseModel):
    name: str
    external_id: str
    tenant_id: int

class DeviceOut(BaseModel):
    id: int; name: str; external_id: str; tenant_id: int; token: str
    class Config: from_attributes = True

class TelemetryIn(BaseModel):
    token: str
    ts: Optional[datetime] = None
    data: Dict[str, Any]

class TelemetryQuery(BaseModel):
    device_id: int
    limit: int = 100
