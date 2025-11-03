from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..utils.rbac import require_role
from ..models_rbac import RoleEnum
from ..database import get_db
from ..auth import get_current_user
from ..models import Telemetry, Device  # Modelos existentes

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


# ==========
# Schemas
# ==========
class _TelemetryQuery(BaseModel):
    device_id: int
    limit: int = Field(default=100, ge=1, le=1000)
    start_ts: Optional[datetime] = Field(default=None, description="ISO8601 (UTC) desde")
    end_ts:   Optional[datetime] = Field(default=None, description="ISO8601 (UTC) hasta")
    keys: Optional[List[str]] = Field(default=None, description="Claves a extraer de data (p.ej. gps, io.Speed)")


# ==========
# Utilidades
# ==========
def _project_keys(data: Dict[str, Any], keys: Optional[List[str]]) -> Dict[str, Any]:
    if not keys:
        return data
    out: Dict[str, Any] = {}
    for k in keys:
        cur: Any = data
        ok = True
        for part in k.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok:
            out[k] = cur
    return out


def _validate_device_in_tenant(db: Session, device_id: int, tenant_id: int) -> Device:
    device = (
        db.query(Device)
        .filter(Device.id == device_id, Device.tenant_id == tenant_id)
        .first()
    )
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device no encontrado en tu tenant",
        )
    return device


# ===========================
# POST /telemetry/query (tu endpoint original con mejoras mínimas)
# ===========================
@router.post(
    "/query",
    dependencies=[Depends(require_role(RoleEnum.viewer))],
)
def query_telemetry(
    q: _TelemetryQuery,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Devuelve telemetría para un device del tenant del usuario,
    con filtros de tiempo opcionales, ordenado por ts DESC.
    """

    hard_max = 1000
    limit = max(1, min(q.limit or 100, hard_max))

    _validate_device_in_tenant(db, q.device_id, user.tenant_id)

    filters = [
        Telemetry.tenant_id == user.tenant_id,
        Telemetry.device_id == q.device_id,
    ]
    if q.start_ts is not None:
        filters.append(Telemetry.ts >= q.start_ts)
    if q.end_ts is not None:
        filters.append(Telemetry.ts <= q.end_ts)

    items: List[Telemetry] = (
        db.query(Telemetry)
        .filter(and_(*filters))
        .order_by(desc(Telemetry.ts))
        .limit(limit)
        .all()
    )

    return [{"ts": t.ts.isoformat(), "data": _project_keys(t.data, q.keys)} for t in items]


# ===========================
# GET /telemetry/devices/{imei}/latest
# ===========================
@router.get(
    "/devices/{imei}/latest",
    dependencies=[Depends(require_role(RoleEnum.viewer))],
)
def get_latest_by_imei(
    imei: str,
    keys: Optional[List[str]] = Query(None, description="Claves opcionales a proyectar, ej: io.IButton, io.IButton_Reverse"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Último punto para un dispositivo del tenant, referenciado por IMEI (Device.external_id).
    """

    device: Optional[Device] = (
        db.query(Device)
        .filter(Device.external_id == imei, Device.tenant_id == user.tenant_id)
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="IMEI no encontrado en tu tenant")

    row: Optional[Telemetry] = (
        db.query(Telemetry)
        .filter(
            Telemetry.tenant_id == user.tenant_id,
            Telemetry.device_id == device.id,
        )
        .order_by(desc(Telemetry.ts))
        .limit(1)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Sin registros para ese IMEI")

    return {
        "imei": imei,
        "device_id": device.id,
        "ts": row.ts.isoformat(),
        "data": _project_keys(row.data, keys),
    }


# ===========================
# GET /telemetry/devices/{imei}
# ===========================
@router.get(
    "/devices/{imei}",
    dependencies=[Depends(require_role(RoleEnum.viewer))],
)
def list_by_imei(
    imei: str,
    limit: int = Query(100, ge=1, le=1000),
    start_ts: Optional[datetime] = Query(None, description="ISO8601 (UTC) desde"),
    end_ts:   Optional[datetime] = Query(None, description="ISO8601 (UTC) hasta"),
    keys: Optional[List[str]] = Query(None, description="Claves a proyectar (ej. gps, io.Speed, io.IButton)"),
    offset: int = Query(0, ge=0, description="Paginación por offset"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Histórico por IMEI con filtros de tiempo y proyección de claves.
    """

    device: Optional[Device] = (
        db.query(Device)
        .filter(Device.external_id == imei, Device.tenant_id == user.tenant_id)
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="IMEI no encontrado en tu tenant")

    filters = [
        Telemetry.tenant_id == user.tenant_id,
        Telemetry.device_id == device.id,
    ]
    if start_ts is not None:
        filters.append(Telemetry.ts >= start_ts)
    if end_ts is not None:
        filters.append(Telemetry.ts <= end_ts)

    rows: List[Telemetry] = (
        db.query(Telemetry)
        .filter(and_(*filters))
        .order_by(desc(Telemetry.ts))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "imei": imei,
        "device_id": device.id,
        "count": len(rows),
        "next_offset": (offset + len(rows)) if len(rows) == limit else None,
        "items": [{"ts": r.ts.isoformat(), "data": _project_keys(r.data, keys)} for r in rows],
    }
