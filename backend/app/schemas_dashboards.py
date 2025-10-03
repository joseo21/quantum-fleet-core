from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict, List
from datetime import datetime


# === Dashboard ===
class DashboardBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False


class DashboardCreate(DashboardBase):
    pass


class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class DashboardOut(DashboardBase):
    id: int
    tenant_id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # Pydantic v2: habilita lectura desde ORM
    model_config = ConfigDict(from_attributes=True)


# === Panel ===
class PanelBase(BaseModel):
    title: str
    type: str  # "timeseries" | "stat" | "table" | ...
    config: Dict[str, Any] = {}
    x: int = 0
    y: int = 0
    w: int = 6
    h: int = 4


class PanelCreate(PanelBase):
    pass


class PanelUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    x: Optional[int] = None
    y: Optional[int] = None
    w: Optional[int] = None
    h: Optional[int] = None


class PanelOut(PanelBase):
    id: int
    dashboard_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# === Dashboard con Panels embebidos ===
class DashboardWithPanels(DashboardOut):
    panels: List[PanelOut] = []
