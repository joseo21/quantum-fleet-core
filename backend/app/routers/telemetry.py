from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..utils.rbac import require_role
from ..models_rbac import RoleEnum
from ..database import get_db
from ..auth import get_current_user
from ..models import Telemetry, Device  # asumo que ya existen estos modelos
from ..schemas import TelemetryQuery    # asumo que tiene: device_id:int, limit:int=100
                                        # Si no tuviera fechas, las añadimos abajo

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


# Si tu TelemetryQuery aún no tiene filtros temporales, puedes crear
# un mini schema aquí sin tocar el original:
try:
    from pydantic import BaseModel, Field
    class _TelemetryQuery(TelemetryQuery):  # extiende el tuyo
        start_ts: Optional[datetime] = Field(default=None, description="ISO8601 (UTC) desde")
        end_ts:   Optional[datetime] = Field(default=None, description="ISO8601 (UTC) hasta")
        keys: Optional[List[str]] = Field(default=None, description="Claves a extraer de data (p.ej. gps, io.Speed)")
except Exception:
    # Fallback (si prefieres no depender del TelemetryQuery existente)
    from pydantic import BaseModel, Field
    class _TelemetryQuery(BaseModel):
        device_id: int
        limit: int = Field(default=100, ge=1, le=1000)
        start_ts: Optional[datetime] = None
        end_ts:   Optional[datetime] = None
        keys: Optional[List[str]] = None


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
    Devuelve la telemetría más reciente para un device del tenant del usuario,
    con filtros de tiempo opcionales.
    """

    # 0) Normaliza / acota el limit
    hard_max = 1000
    limit = max(1, min(q.limit or 100, hard_max))

    # 1) Validar que el device pertenece al tenant actual
    device = (
        db.query(Device)
        .filter(Device.id == q.device_id, Device.tenant_id == user.tenant_id)
        .first()
    )
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device no encontrado en tu tenant",
        )

    # 2) Construir filtros
    filters = [
        Telemetry.tenant_id == user.tenant_id,
        Telemetry.device_id == q.device_id,
    ]
    if q.start_ts is not None:
        filters.append(Telemetry.ts >= q.start_ts)
    if q.end_ts is not None:
        filters.append(Telemetry.ts <= q.end_ts)

    # 3) Query
    items: List[Telemetry] = (
        db.query(Telemetry)
        .filter(and_(*filters))
        .order_by(desc(Telemetry.ts))
        .limit(limit)
        .all()
    )

    # 4) Post-procesamiento opcional de `data` si pidieron `keys`
    def project(data: Dict[str, Any]) -> Dict[str, Any]:
        if not q.keys:
            return data
        out: Dict[str, Any] = {}
        for k in q.keys:
            # Soporta "io.Speed" (anidado) y "gps"
            cur = data
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

    # 5) Respuesta
    return [{"ts": t.ts.isoformat(), "data": project(t.data)} for t in items]

