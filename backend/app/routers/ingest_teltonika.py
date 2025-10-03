from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy import text, bindparam
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.database import get_db  # <-- ya lo tienes en tu proyecto
from app.parsers.teltonika.teltonika_FMC650 import parse_io

router = APIRouter(prefix="/ingest/teltonika", tags=["ingest: teltonika"])


# ========= Pydantic =========
class GPSPayload(BaseModel):
    lat: float
    lon: float
    speed: Optional[float] = None


class FMC650Payload(BaseModel):
    # Opción A: autenticación por token de dispositivo (ver header)
    device_external_id: Optional[str] = Field(
        None,
        description="Identificador externo del device (si NO usas X-Device-Token)",
    )
    timestamp: Optional[datetime] = None
    gps: Optional[GPSPayload] = None
    io: Dict[str, Any] = Field(default_factory=dict)

    @validator("timestamp", pre=True)
    def _parse_ts(cls, v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            # epoch seconds
            return datetime.fromtimestamp(v, tz=timezone.utc)
        if isinstance(v, str):
            # ISO8601
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


# ========= Helpers DB =========
def _find_device_by_token(db: Session, tenant_id: int, token: str) -> Optional[int]:
    row = db.execute(
        text("SELECT id FROM devices WHERE tenant_id=:t AND token=:tok"),
        {"t": tenant_id, "tok": token},
    ).first()
    return int(row[0]) if row else None


def _find_device_by_external_id(db: Session, tenant_id: int, ext: str) -> Optional[int]:
    row = db.execute(
        text("SELECT id FROM devices WHERE tenant_id=:t AND external_id=:e"),
        {"t": tenant_id, "e": ext},
    ).first()
    return int(row[0]) if row else None


# ========= Endpoint =========
@router.post("/FMC650")
def ingest_fmc650(
    payload: FMC650Payload,
    db: Session = Depends(get_db),
    x_tenant_id: int = Header(..., alias="X-Tenant-ID"),
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
):
    """
    Ingesta para Teltonika FMC650.

    Autenticación soportada:
      - **X-Device-Token** (recomendada para dispositivos en campo)
      - o bien **device_external_id** + autorización bearer del operador.

    Guarda un registro en `telemetry` con:
      - tenant_id, device_id
      - ts (UTC, ahora si no viene)
      - data JSONB con: { "gps": {...}, "io": {...}, "rejected_io": {...} }
    """
    # 1) Resolver device_id
    device_id: Optional[int] = None
    if x_device_token:
        device_id = _find_device_by_token(db, x_tenant_id, x_device_token)
        if not device_id:
            raise HTTPException(status_code=401, detail="X-Device-Token inválido")
    else:
        if not payload.device_external_id:
            raise HTTPException(
                status_code=400,
                detail="Falta X-Device-Token o `device_external_id` en el body",
            )
        device_id = _find_device_by_external_id(db, x_tenant_id, payload.device_external_id)
        if not device_id:
            raise HTTPException(status_code=404, detail="Device no encontrado")

    # 2) Timestamp
    ts = payload.timestamp or datetime.now(tz=timezone.utc)

    # 3) Parseo de IO (solo IDs válidos)
    io_mapped, io_rejected = parse_io(payload.io or {})

    # 4) Build JSON a guardar
    data_to_save: Dict[str, Any] = {}
    if payload.gps:
        data_to_save["gps"] = payload.gps.dict()
    if io_mapped:
        data_to_save["io"] = io_mapped
    if io_rejected:
        data_to_save["rejected_io"] = io_rejected

    # 5) Insert (JSONB seguro con bindparam)
    stmt = (
        text(
            "INSERT INTO telemetry (tenant_id, device_id, ts, data) "
            "VALUES (:t, :d, :ts, :data)"
        )
        .bindparams(bindparam("data", type_=JSONB))
    )

    db.execute(
        stmt,
        {
            "t": x_tenant_id,
            "d": device_id,
            "ts": ts.replace(tzinfo=None),  # tu tabla es naive (sin TZ)
            "data": data_to_save,           # dict -> JSONB (ok)
        },
    )
    db.commit()

    return {
        "status": "ok",
        "tenant_id": x_tenant_id,
        "device_id": device_id,
        "saved_keys": list(data_to_save.keys()),
        "rejected_count": len(io_rejected),
    }
