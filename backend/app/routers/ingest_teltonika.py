from __future__ import annotations

import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB

from app.database import get_db
from app.models import Device

log = logging.getLogger("ingest.teltonika")

# Auth opcional: si no existe, continuamos anónimo (NO bloquea la ingesta)
try:
    from app.auth import get_current_user_optional  # type: ignore
except Exception:
    def get_current_user_optional():
        return None  # type: ignore

# Parser Teltonika opcional: si no existe, dejamos io tal cual
try:
    from app.parsers.teltonika.teltonika_FMC650 import parse_io  # type: ignore
except Exception:
    def parse_io(io: Dict[str, Any]):
        return (io or {}), {}  # mapped, rejected


router = APIRouter(prefix="/ingest/teltonika", tags=["ingest: teltonika"])


class GPS(BaseModel):
    lat: float
    lon: float
    speed: Optional[float] = None
    sat: Optional[int] = None
    hdop: Optional[float] = None


class TeltonikaIn(BaseModel):
    token: Optional[str] = None
    external_id: Optional[str] = None
    ts: Optional[Any] = None   # epoch ms o ISO8601
    gps: Optional[GPS] = None
    io: Optional[Dict[str, Any]] = None
    batch: Optional[List[Dict[str, Any]]] = None  # [{ts, gps, io}, ...]

    @validator("ts", pre=True)
    def _norm_ts(cls, v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            # Acepta "2025-10-08T12:34:56Z" etc.
            try:
                return int(datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp() * 1000)
            except Exception:
                return None
        return None


def _ts_to_datetime(ts_ms: Optional[int]) -> datetime:
    if ts_ms is None:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)


def _resolve_device(
    db: Session,
    tenant_id: Optional[int],
    token: Optional[str],
    external_id: Optional[str],
) -> Device:
    if not token and not external_id:
        raise HTTPException(status_code=400, detail="Falta token o external_id")

    q = db.query(Device)
    if token:
        q = q.filter(Device.token == token)
    if external_id:
        q = q.filter(Device.external_id == external_id)
    # Filtra por tenant SOLO si viene informado (con auth)
    if tenant_id is not None:
        q = q.filter(Device.tenant_id == tenant_id)

    dev = q.first()
    if not dev:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dev


@router.get("/ping")
def ping():
    return {"status": "ok"}


@router.post("/ingest")
def ingest_one(
    payload: TeltonikaIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_optional),
):
    try:
        # tenant del contexto (si el auth opcional lo aporta)
        ctx_tenant_id: Optional[int] = None
        if user is not None and hasattr(user, "tenant_id") and user.tenant_id is not None:
            try:
                ctx_tenant_id = int(user.tenant_id)
            except Exception:
                ctx_tenant_id = None

        # Valida batch vs single
        if payload.batch and (payload.gps or payload.io):
            raise HTTPException(status_code=400, detail="Usa batch o single (gps/io), no ambos.")

        # Resuelve device por token/external_id (+tenant si lo hay)
        dev = _resolve_device(db, ctx_tenant_id, payload.token, payload.external_id)

        # Statement con binder JSONB (no usamos ::jsonb, dejamos que el driver lo maneje)
        stmt = text("""
            INSERT INTO telemetry (tenant_id, device_id, ts, data)
            VALUES (:tenant_id, :device_id, :ts, :data)
        """)

        # Forzamos type_ JSONB para que psycopg3 serialice dict -> jsonb
        stmt = stmt.bindparams(
            bindparam("tenant_id"),
            bindparam("device_id"),
            bindparam("ts"),
            bindparam("data", type_=JSONB),
        )

        def _save_row(ts_ms: Optional[int], gps_obj: Optional[GPS], io_obj: Dict[str, Any]):
            io_mapped, io_rejected = parse_io(io_obj or {})
            blob: Dict[str, Any] = {}
            if gps_obj:
                blob["gps"] = gps_obj.dict()
            if io_mapped:
                blob["io"] = io_mapped
            if io_rejected:
                blob["rejected_io"] = io_rejected

            db.execute(
                stmt,
                {
                    "tenant_id": dev.tenant_id,
                    "device_id": dev.id,
                    "ts": _ts_to_datetime(ts_ms),
                    "data": blob,  # ✅ dict -> JSONB via binder
                },
            )

        if not payload.batch:
            _save_row(payload.ts, payload.gps, payload.io or {})
            db.commit()
            return {"status": "ok", "device_id": dev.id, "tenant_id": dev.tenant_id}

        # batch
        for item in payload.batch:
            ts_item = item.get("ts", payload.ts)
            gps_item = item.get("gps")
            io_item = item.get("io", {})
            gps_model = GPS(**gps_item) if isinstance(gps_item, dict) else None
            _save_row(ts_item, gps_model, io_item)

        db.commit()
        return {"status": "ok", "ingested": len(payload.batch), "device_id": dev.id, "tenant_id": dev.tenant_id}

    except HTTPException:
        # Propaga 4xx tal cual
        raise
    except Exception as e:
        # Log detallado del 500 para depurar rápido
        log.error("Ingest error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal error in ingest")
