from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from app.database import get_db
from app.models import Device

router = APIRouter(tags=["telemetry"], prefix="/telemetry")

def _to_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        # acepta ISO (yyyy-mm-ddThh:mm:ssZ) o ms unix
        if s.isdigit():
            return datetime.fromtimestamp(int(s)/1000.0, tz=timezone.utc)
        return datetime.fromisoformat(s.replace("Z","+00:00"))
    except Exception:
        return None

@router.get("/query")
def get_telemetry(
    db: Session = Depends(get_db),
    external_id: Optional[str] = Query(None),
    device_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    frm: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    order: str = Query("desc", pattern="^(desc|asc)$"),
):
    if not external_id and not device_id:
        raise HTTPException(status_code=400, detail="Debes enviar external_id o device_id")

    if external_id and not device_id:
        dev = db.query(Device).filter(Device.external_id == external_id).first()
        if not dev:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        device_id = dev.id

    dt_from = _to_dt(frm)
    dt_to = _to_dt(to)
    if dt_to and dt_from and dt_to < dt_from:
        raise HTTPException(status_code=400, detail="Rango de tiempo inválido")

    # Fallbacks de rango si no se envían
    if not dt_to:
        dt_to = datetime.now(timezone.utc)
    if not dt_from:
        # últimas 24h por defecto
        dt_from = datetime.fromtimestamp(dt_to.timestamp() - 24*3600, tz=timezone.utc)

    stmt = text(f"""
        SELECT ts, data
        FROM telemetry
        WHERE device_id = :device_id
          AND ts >= :from_ts
          AND ts <= :to_ts
        ORDER BY ts {"DESC" if order=="desc" else "ASC"}
        LIMIT :limit
    """)
    rows = db.execute(
        stmt.bindparams(
            bindparam("device_id", value=device_id),
            bindparam("from_ts", value=dt_from),
            bindparam("to_ts", value=dt_to),
            bindparam("limit", value=limit),
        )
    ).fetchall()

    # Normalizamos la salida
    out = [{"ts": r[0].isoformat(), **(r[1] if isinstance(r[1], dict) else {"data": r[1]})} for r in rows]
    return out
