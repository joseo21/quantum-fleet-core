from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from typing import Any, Optional, List

import psycopg
from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()

# ----------------------------
# Util DB
# ----------------------------
def _dsn() -> str:
    """
    Construye un DSN válido para psycopg a partir de variables de entorno.
    Acepta DATABASE_URL estilo SQLAlchemy (postgresql+psycopg://) y lo normaliza.
    """
    url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI") or ""
    if url.startswith("postgresql+psycopg://"):
        url = "postgresql://" + url.split("postgresql+psycopg://", 1)[1]
        return url

    host = os.getenv("POSTGRES_HOST") or os.getenv("PGHOST") or "postgres"
    port = os.getenv("POSTGRES_PORT") or os.getenv("PGPORT") or "5432"
    db   = os.getenv("POSTGRES_DB")   or os.getenv("PGDATABASE") or "quantumfleet"
    user = os.getenv("POSTGRES_USER") or os.getenv("PGUSER") or "quantum"
    pwd  = os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD") or "quantum123"
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

def db_connect():
    return psycopg.connect(_dsn(), autocommit=True)

def _table_exists(cur, schema: str, name: str) -> bool:
    cur.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name=%s",
        (schema, name),
    )
    return cur.fetchone() is not None

# ----------------------------
# Modelos
# ----------------------------
class AuditEventIn(BaseModel):
    tenant_id: Optional[int] = None
    actor_type: str
    actor_id: Optional[str] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    meta: dict = Field(default_factory=dict)

class AuditEventOut(AuditEventIn):
    id: int
    at: datetime

# ----------------------------
# Helpers de sesiones
# ----------------------------
def _device_id_by_external_id(cur, external_id: str) -> Optional[int]:
    cur.execute("SELECT id FROM public.devices WHERE external_id=%s", (external_id,))
    row = cur.fetchone()
    return row[0] if row else None

def _now_tz() -> datetime:
    return datetime.now(timezone.utc)

def _open_device_session(cur, device_id: int, remote_addr: Optional[str]):
    # cierra previas abiertas
    cur.execute(
        "UPDATE public.device_sessions SET ended_at=now() WHERE device_id=%s AND ended_at IS NULL",
        (device_id,),
    )
    cur.execute(
        """
        INSERT INTO public.device_sessions (device_id, started_at, last_seen_at, remote_addr)
        VALUES (%s, now(), now(), %s)
        """,
        (device_id, remote_addr),
    )

def _touch_device_session(cur, device_id: int):
    cur.execute(
        "UPDATE public.device_sessions SET last_seen_at=now() WHERE device_id=%s AND ended_at IS NULL",
        (device_id,),
    )

def _close_device_session(cur, device_id: int):
    cur.execute(
        """
        UPDATE public.device_sessions
        SET last_seen_at = COALESCE(last_seen_at, now()), ended_at = COALESCE(ended_at, now())
        WHERE device_id=%s AND ended_at IS NULL
        """,
        (device_id,),
    )

def _int_or_none(s: Optional[str]) -> Optional[int]:
    try:
        return int(s) if s is not None else None
    except Exception:
        return None

def _open_user_session(cur, user_id: int, ip: Optional[str], user_agent: Optional[str]):
    # si la tabla existe, gestiona la sesión
    if not _table_exists(cur, "public", "user_sessions"):
        return
    cur.execute(
        "UPDATE public.user_sessions SET ended_at=now() WHERE user_id=%s AND ended_at IS NULL",
        (user_id,),
    )
    cur.execute(
        """
        INSERT INTO public.user_sessions (user_id, started_at, last_seen_at, ip, user_agent)
        VALUES (%s, now(), now(), %s, %s)
        """,
        (user_id, ip, user_agent),
    )

def _touch_user_session(cur, user_id: int):
    if not _table_exists(cur, "public", "user_sessions"):
        return
    cur.execute(
        "UPDATE public.user_sessions SET last_seen_at=now() WHERE user_id=%s AND ended_at IS NULL",
        (user_id,),
    )

def _close_user_session(cur, user_id: int):
    if not _table_exists(cur, "public", "user_sessions"):
        return
    cur.execute(
        "UPDATE public.user_sessions SET ended_at=now() WHERE user_id=%s AND ended_at IS NULL",
        (user_id,),
    )

# ----------------------------
# Endpoints
# ----------------------------
@router.post("/audit/events", response_model=AuditEventOut, summary="Create Audit Event")
def create_audit_event(event: AuditEventIn, request: Request) -> AuditEventOut:
    """
    Inserta un evento de auditoría y, como side-effect:
      - device.connected: abre sesión de dispositivo (cierra previas abiertas).
      - device.keepalive/device.message: refresca last_seen.
      - device.disconnected: cierra sesión abierta.
      - user.login: abre sesión de usuario (sin depender de public.users).
      - user.keepalive: refresca last_seen.
      - user.logout: cierra sesión abierta.
    """
    # elegir IP a guardar
    ip_to_store = event.ip or (request.client.host if request.client else None)
    ua_to_store = event.user_agent or request.headers.get("User-Agent")

    try:
        with db_connect() as conn, conn.cursor() as cur:
            # 1) insert audit
            cur.execute(
                """
                INSERT INTO public.audit_events
                    (tenant_id, actor_type, actor_id, action, target_type, target_id, ip, user_agent, meta)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING id, at
                """,
                (
                    event.tenant_id,
                    event.actor_type,
                    event.actor_id,
                    event.action,
                    event.target_type,
                    event.target_id,
                    ip_to_store,
                    ua_to_store,
                    json.dumps(event.meta or {}),
                ),
            )
            row = cur.fetchone()
            ev_id, at = row[0], row[1]

            # 2) efectos secundarios: device sessions
            if (event.actor_type or "").lower() == "device" and event.actor_id:
                device_id = _device_id_by_external_id(cur, event.actor_id)
                if device_id is not None:
                    action = (event.action or "").lower()
                    remote_addr = (event.meta or {}).get("remote_addr")
                    if action == "device.connected":
                        _open_device_session(cur, device_id, remote_addr)
                    elif action in ("device.keepalive", "device.message"):
                        _touch_device_session(cur, device_id)
                    elif action in ("device.disconnected", "device.timeout", "device.error"):
                        _close_device_session(cur, device_id)

            # 3) efectos secundarios: user sessions (opcional, sin FK)
            if (event.actor_type or "").lower() == "user" and event.actor_id:
                uid = _int_or_none(event.actor_id)
                if uid is not None:
                    action = (event.action or "").lower()
                    if action == "user.login":
                        _open_user_session(cur, uid, ip_to_store, ua_to_store)
                    elif action in ("user.keepalive", "user.activity"):
                        _touch_user_session(cur, uid)
                    elif action in ("user.logout",):
                        _close_user_session(cur, uid)

        # respuesta
        return AuditEventOut(
            id=ev_id,
            at=at,
            tenant_id=event.tenant_id,
            actor_type=event.actor_type,
            actor_id=event.actor_id,
            action=event.action,
            target_type=event.target_type,
            target_id=event.target_id,
            ip=ip_to_store,
            user_agent=ua_to_store,
            meta=event.meta or {},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error creando evento: {e}")

@router.get("/audit/events", response_model=List[AuditEventOut], summary="List Audit Events")
def list_audit_events(
    tenant_id: Optional[int] = Query(default=None),
    actor_type: Optional[str] = Query(default=None),
    actor_id: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    target_type: Optional[str] = Query(default=None),
    target_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
):
    """
    Lista eventos con filtros opcionales.
    NOTA: `ip::text` para que Pydantic reciba string (evita IPv4Address).
    """
    try:
        clauses = []
        params: list[Any] = []
        if tenant_id is not None:
            clauses.append("tenant_id = %s")
            params.append(tenant_id)
        if actor_type:
            clauses.append("actor_type = %s")
            params.append(actor_type)
        if actor_id:
            clauses.append("actor_id = %s")
            params.append(actor_id)
        if action:
            clauses.append("action = %s")
            params.append(action)
        if target_type:
            clauses.append("target_type = %s")
            params.append(target_type)
        if target_id:
            clauses.append("target_id = %s")
            params.append(target_id)

        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        sql = f"""
            SELECT
              id, at, tenant_id, actor_type, actor_id, action, target_type, target_id,
              ip::text AS ip, user_agent, COALESCE(meta, '{{}}'::jsonb) AS meta
            FROM public.audit_events
            {where}
            ORDER BY at DESC
            LIMIT %s
        """
        params.append(limit)

        out: List[AuditEventOut] = []
        with db_connect() as conn, conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            for r in cur.fetchall():
                out.append(
                    AuditEventOut(
                        id=r[0],
                        at=r[1],
                        tenant_id=r[2],
                        actor_type=r[3],
                        actor_id=r[4],
                        action=r[5],
                        target_type=r[6],
                        target_id=r[7],
                        ip=r[8],
                        user_agent=r[9],
                        meta=r[10] or {},
                    )
                )
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error listando eventos: {e}")
