# backend/app/routers/connectors.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

import httpx
import psycopg
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel

router = APIRouter(tags=["connectors"])

# --------------------------------------------------------------------
# DSN / Conexión Postgres (psycopg3)
# --------------------------------------------------------------------
def _dsn() -> str:
    """
    Normaliza DATABASE_URL para psycopg.connect.
    Acepta 'postgresql+psycopg://' (SQLAlchemy) y lo convierte a 'postgresql://'.
    Si no hay DATABASE_URL, arma el DSN desde variables de entorno.
    """
    url = os.getenv("DATABASE_URL")
    if url:
        if url.startswith("postgresql+psycopg://"):
            url = url.replace("postgresql+psycopg://", "postgresql://", 1)
        if url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://", 1)
        return url

    host = os.getenv("PGHOST") or os.getenv("DB_HOST") or os.getenv("POSTGRES_HOST") or "postgres"
    port = os.getenv("PGPORT") or os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT") or "5432"
    db   = os.getenv("PGDATABASE") or os.getenv("DB_NAME") or os.getenv("POSTGRES_DB") or "quantumfleet"
    usr  = os.getenv("PGUSER") or os.getenv("DB_USER") or os.getenv("POSTGRES_USER") or "quantum"
    pwd  = os.getenv("PGPASSWORD") or os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD") or "quantum"
    return f"postgresql://{usr}:{pwd}@{host}:{port}/{db}"


def db_connect():
    return psycopg.connect(_dsn(), autocommit=True)


# --------------------------------------------------------------------
# Bootstrap de esquema (idempotente)
# --------------------------------------------------------------------
_BOOTSTRAPPED = False

def _bootstrap_schema():
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute("""
CREATE TABLE IF NOT EXISTS public.connectors (
  id            SERIAL PRIMARY KEY,
  name          TEXT UNIQUE NOT NULL,
  base_url      TEXT,
  auth_type     TEXT NOT NULL DEFAULT 'none', -- none|header|bearer|query
  auth_token    TEXT,
  headers       JSONB NOT NULL DEFAULT '{}'::jsonb,
  params        JSONB NOT NULL DEFAULT '{}'::jsonb,
  webhook_token TEXT UNIQUE,
  mapping       JSONB NOT NULL DEFAULT '{}'::jsonb,
  enabled       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
""")
        cur.execute("""
CREATE TABLE IF NOT EXISTS public.connector_logs (
  id            BIGSERIAL PRIMARY KEY,
  connector_id  INTEGER REFERENCES public.connectors(id) ON DELETE CASCADE,
  at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  direction     TEXT NOT NULL,         -- 'out'|'in'
  status        INTEGER,
  method        TEXT,
  path          TEXT,
  request       JSONB,
  response      JSONB
);
""")
        # Asegurar columnas si existía una versión vieja
        cur.execute("""
ALTER TABLE public.connectors
  ADD COLUMN IF NOT EXISTS headers JSONB NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS params  JSONB NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS webhook_token TEXT,
  ADD COLUMN IF NOT EXISTS mapping JSONB NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS enabled BOOLEAN NOT NULL DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();
""")
        cur.execute("""CREATE INDEX IF NOT EXISTS ix_connectors_enabled ON public.connectors (enabled);""")
        cur.execute("""CREATE INDEX IF NOT EXISTS ix_connector_logs_connector_at ON public.connector_logs (connector_id, at DESC);""")
    _BOOTSTRAPPED = True


# --------------------------------------------------------------------
# Modelos (request/response)
# --------------------------------------------------------------------
class ConnectorCreate(BaseModel):
    name: str
    base_url: Optional[str] = None
    auth_type: str = "none"      # none|header|bearer|query
    auth_token: Optional[str] = None
    headers: Dict[str, Any] = {}
    params: Dict[str, Any] = {}
    webhook_token: Optional[str] = None
    mapping: Dict[str, Any] = {}
    enabled: bool = True


class ConnectorCall(BaseModel):
    method: str
    path: str
    query: Dict[str, Any] = {}
    headers: Dict[str, Any] = {}
    body: Any | None = None


def _mask(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    return "***" if len(value) <= 8 else (value[:2] + "****" + value[-2:])


def _join_url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"

def _build_auth(auth_type: str, auth_token: Optional[str], headers: Dict[str, str], params: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, Any]]:
    if auth_type == "bearer" and auth_token:
        headers = dict(headers or {})
        headers["Authorization"] = f"Bearer {auth_token}"
    elif auth_type == "header" and auth_token:
        headers = dict(headers or {})
        headers["X-API-KEY"] = auth_token
    elif auth_type == "query" and auth_token:
        params = dict(params or {})
        params["apikey"] = auth_token
    return headers, params

def _log(conn, connector_id: int, direction: str, status_code: int, method: str, path: str, request: Dict[str, Any], response: Dict[str, Any]):
    with conn.cursor() as cur:
        cur.execute(
            """
INSERT INTO public.connector_logs (connector_id, direction, status, method, path, request, response)
VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
""",
            (connector_id, direction, status_code, method, path, json.dumps(request), json.dumps(response)),
        )

def _get_in(obj: Any, dotted_path: Optional[str]) -> Any:
    if obj is None or dotted_path is None:
        return None
    p = dotted_path.strip()
    if not p:
        return None
    if p.startswith("$."):
        p = p[2:]
    cur = obj
    for key in [k for k in p.split(".") if k]:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur

def _ingest_telemetry_via_api(payload: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
    base = os.getenv("API_BASE", "http://api:8000")
    urls = [
        _join_url(base, "ingest/http"),
        _join_url(base, "ingest/teltonika/ingest"),
    ]
    last_status = 0
    last_body: Dict[str, Any] = {}
    with httpx.Client(timeout=5.0) as client:
        for url in urls:
            try:
                r = client.post(url, json=payload)
                last_status = r.status_code
                try:
                    last_body = r.json()
                except Exception:
                    last_body = {"raw": r.text}
                if 200 <= r.status_code < 300:
                    return r.status_code, last_body
            except Exception as e:
                last_status = 0
                last_body = {"error": str(e)}
    return last_status or 599, last_body


# --------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------
@router.post("/connectors", summary="Create Or Update Connector", description="Upsert por 'name'. Devuelve {id, name, ...}.")
def create_or_update_connector(body: ConnectorCreate):
    _bootstrap_schema()
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
INSERT INTO public.connectors (name, base_url, auth_type, auth_token, headers, params, webhook_token, mapping, enabled)
VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s::jsonb, %s)
ON CONFLICT (name) DO UPDATE SET
  base_url = EXCLUDED.base_url,
  auth_type = EXCLUDED.auth_type,
  auth_token = EXCLUDED.auth_token,
  headers = EXCLUDED.headers,
  params = EXCLUDED.params,
  webhook_token = EXCLUDED.webhook_token,
  mapping = EXCLUDED.mapping,
  enabled = EXCLUDED.enabled
RETURNING id, name, base_url, auth_type, auth_token, headers, params, webhook_token, mapping, enabled, created_at;
""",
            (
                body.name,
                body.base_url,
                body.auth_type,
                body.auth_token,
                json.dumps(body.headers or {}),
                json.dumps(body.params or {}),
                body.webhook_token,
                json.dumps(body.mapping or {}),
                body.enabled,
            ),
        )
        row = cur.fetchone()
        return {
            "id": row[0],
            "name": row[1],
            "base_url": row[2],
            "auth_type": row[3],
            "auth_token": _mask(row[4]),
            "headers": row[5],
            "params": row[6],
            "webhook_token": row[7],
            "mapping": row[8],
            "enabled": row[9],
            "created_at": row[10].isoformat() if row[10] else None,
        }


@router.get("/connectors", summary="List Connectors")
def list_connectors():
    _bootstrap_schema()
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute("""
SELECT id, name, base_url, auth_type, auth_token, headers, params, webhook_token, mapping, enabled, created_at
FROM public.connectors
ORDER BY id ASC;
""")
        return [
            {
                "id": r[0],
                "name": r[1],
                "base_url": r[2],
                "auth_type": r[3],
                "auth_token": _mask(r[4]),
                "headers": r[5],
                "params": r[6],
                "webhook_token": r[7],
                "mapping": r[8],
                "enabled": r[9],
                "created_at": r[10].isoformat() if r[10] else None,
            }
            for r in cur.fetchall()
        ]


@router.post("/connectors/{connector_id}/call", summary="Call external API through a connector")
def call_connector(connector_id: int, body: ConnectorCall):
    _bootstrap_schema()
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
SELECT id, name, base_url, auth_type, auth_token, headers, params, enabled
FROM public.connectors
WHERE id = %s;
""",
            (connector_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector no existe")

        cid, name, base_url, auth_type, auth_token, base_headers, base_params, enabled = row
        if not enabled:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Connector deshabilitado")
        if not base_url:
            raise HTTPException(status_code=400, detail="Connector sin base_url")

        method = body.method.upper().strip()
        url = _join_url(base_url, body.path or "/")

        headers = {**(base_headers or {}), **(body.headers or {})}
        params = {**(base_params or {}), **(body.query or {})}
        headers, params = _build_auth(auth_type, auth_token, headers, params)

        req_log = {
            "url": url,
            "method": method,
            "params": params,
            "headers": {k: ("***" if k.lower() in ("authorization", "x-api-key") else v) for k, v in (headers or {}).items()},
            "body": body.body,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                r = client.request(method, url, params=params, headers=headers, json=body.body)
                status_code = r.status_code
                try:
                    data = r.json()
                    resp_log = {"json": data}
                except Exception:
                    data = None
                    resp_log = {"text": r.text}

                _log(conn, cid, "out", status_code, method, body.path, req_log, resp_log)
                if data is not None:
                    return data
                return {"status": status_code, **resp_log}
        except Exception as e:
            _log(conn, cid, "out", 599, method, body.path, req_log, {"error": str(e)})
            raise HTTPException(status_code=502, detail=f"Error al llamar API externa: {e}")


@router.post("/hooks/{token}", summary="Webhook receiver")
def webhook_receiver(token: str, payload: Dict[str, Any] = Body(...)):
    _bootstrap_schema()
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
SELECT id, name, mapping, enabled
FROM public.connectors
WHERE webhook_token = %s;
""",
            (token,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Token inválido")

        cid, name, mapping, enabled = row
        if not enabled:
            raise HTTPException(status_code=409, detail="Connector deshabilitado")

        _log(conn, cid, "in", 200, "POST", f"/hooks/{token}", {"body": payload}, {"received": True})

        if mapping and mapping.get("emit_telemetry"):
            ext_path = mapping.get("external_id_path")
            ts_path  = mapping.get("ts_path")
            lat_path = mapping.get("gps_lat_path")
            lon_path = mapping.get("gps_lon_path")
            spd_path = mapping.get("gps_speed_path")

            external_id = _get_in(payload, ext_path)
            ts_ms = _get_in(payload, ts_path)
            lat = _get_in(payload, lat_path)
            lon = _get_in(payload, lon_path)
            spd = _get_in(payload, spd_path)

            if not external_id or ts_ms is None:
                raise HTTPException(status_code=400, detail="Mapping incompleto: external_id o ts no presentes")

            ingest_doc: Dict[str, Any] = {
                "external_id": str(external_id),
                "ts": int(ts_ms),
                "gps": {},
            }
            if lat is not None and lon is not None:
                ingest_doc["gps"]["lat"] = float(lat)
                ingest_doc["gps"]["lon"] = float(lon)
            if spd is not None:
                ingest_doc["gps"]["speed"] = float(spd)

            code, resp = _ingest_telemetry_via_api(ingest_doc)
            _log(conn, cid, "out", code, "POST", "/ingest", {"json": ingest_doc}, resp)
            if not (200 <= code < 300):
                raise HTTPException(status_code=502, detail="Error ingestando telemetría")

        return {"status": "ok", "connector_id": cid, "name": name}
