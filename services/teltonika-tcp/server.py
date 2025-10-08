#!/usr/bin/env python3
import asyncio, struct, json, os, logging
from typing import Tuple, Dict, Any, List, Optional

import requests
try:
    import psycopg  # fallback opcional a BD
except Exception:
    psycopg = None

# ----------------------------------------
# Logging
# ----------------------------------------
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("teltonika-tcp")

# ----------------------------------------
# Config API / red
# ----------------------------------------
API_BASE = os.getenv("API_BASE", "http://api:8000").rstrip("/")
INGEST_URL = f"{API_BASE}/ingest/teltonika/ingest"
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5.0"))

# Cabecera multi-tenant opcional
DEFAULT_TENANT_ID = os.getenv("DEFAULT_TENANT_ID")  # ej: "1"

# ----------------------------------------
# Config listener TCP
# ----------------------------------------
LISTEN_HOST = os.getenv("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.getenv("LISTEN_PORT", "5027"))

# ----------------------------------------
# Config fallback BD
# ----------------------------------------
FALLBACK_DB = os.getenv("FALLBACK_DB", "0") == "1"

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "quantumfleet")
DB_USER = os.getenv("DB_USER", "quantum")
DB_PASSWORD = os.getenv("DB_PASSWORD", "quantum")

if FALLBACK_DB and psycopg is None:
    log.warning("FALLBACK_DB=1 pero psycopg no está disponible; se ignorará fallback.")

# ----------------------------------------
# Lectores utilitarios
# ----------------------------------------
def _u8(b: bytes, p: int) -> Tuple[int, int]:
    return b[p], p + 1

def _u16(b: bytes, p: int) -> Tuple[int, int]:
    return struct.unpack(">H", b[p:p+2])[0], p + 2

def _u32(b: bytes, p: int) -> Tuple[int, int]:
    return struct.unpack(">I", b[p:p+4])[0], p + 4

def _i32(b: bytes, p: int) -> Tuple[int, int]:
    return struct.unpack(">i", b[p:p+4])[0], p + 4

def _i64(b: bytes, p: int) -> Tuple[int, int]:
    return struct.unpack(">q", b[p:p+8])[0], p + 8

# ----------------------------------------
# Decoder seguro (codec 0x08 y 0x8E)
# ----------------------------------------
def decode_avl_data(data: bytes) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    data = [codec(1)][n1(1)][records...][n2(1)]
    Devuelve (codec, n2, records). Lanza ValueError si el buffer es inconsistente.
    """
    if len(data) < 3:
        raise ValueError("AVL muy corto")

    codec = data[0]
    if codec not in (0x08, 0x8E):
        raise ValueError(f"Codec no soportado: 0x{codec:02x}")

    n1 = data[1]
    n2 = data[-1]
    end = len(data) - 1  # último índice que no podemos sobrepasar (antes de n2)
    pos = 2

    out: List[Dict[str, Any]] = []

    for _ in range(n1):
        # ts(8) + priority(1)
        if pos + 9 > end:
            raise ValueError("sin espacio para ts/priority")
        ts_ms, pos = _i64(data, pos)
        _prio, pos = _u8(data, pos)

        # GNSS: lon(4) lat(4) alt(2) ang(2) sats(1) speed(2) = 15 bytes
        if pos + 15 > end:
            raise ValueError("sin espacio para GNSS")
        lon, pos = _i32(data, pos)
        lat, pos = _i32(data, pos)
        alt, pos = _u16(data, pos)
        ang, pos = _u16(data, pos)
        sats, pos = _u8(data, pos)
        speed, pos = _u16(data, pos)

        gps = {
            "lat": lat / 1e7,
            "lon": lon / 1e7,
            "alt": int(alt),
            "ang": int(ang),
            "sat": int(sats),
            "speed": float(speed),
        }

        # IO header: event_id (2 bytes en 8E; 1 byte en 08) + total(1)
        # Para simplificar (tolerante): leer 2 bytes si entran; si no, caer a 1 byte.
        if pos + 2 > end:
            raise ValueError("sin espacio para IO header")
        # Intentar 2 bytes (8E)
        event_id = None
        try:
            if codec == 0x8E:
                event_id, pos = _u16(data, pos)
            else:
                # Codec 8 clásico suele usar 1 byte; si usamos 2, puede quedar inconsistente.
                eid, pos_try = _u8(data, pos)
                event_id, pos = int(eid), pos_try
        except Exception:
            # Fallback extremo: un byte
            eid, pos = _u8(data, pos)
            event_id = int(eid)

        if pos + 1 > end:
            raise ValueError("sin espacio para IO total")
        _total, pos = _u8(data, pos)

        # IO por tamaños
        io: Dict[str, Any] = {}

        n1b, pos = _u8(data, pos)
        for _ in range(n1b):
            kid, pos = _u8(data, pos)
            val, pos = _u8(data, pos)
            io[str(kid)] = int(val)

        n2b, pos = _u8(data, pos)
        for _ in range(n2b):
            kid, pos = _u8(data, pos)
            val, pos = _u16(data, pos)
            io[str(kid)] = int(val)

        n4b, pos = _u8(data, pos)
        for _ in range(n4b):
            kid, pos = _u8(data, pos)
            val, pos = _i32(data, pos)
            io[str(kid)] = int(val)

        n8b, pos = _u8(data, pos)
        for _ in range(n8b):
            kid, pos = _u8(data, pos)
            val, pos = _i64(data, pos)
            io[str(kid)] = int(val)

        out.append({"ts": ts_ms, "gps": gps, "io": io, "event_id": event_id})

    return codec, n2, out

# ----------------------------------------
# Fallback DB helpers
# ----------------------------------------
def db_get_conn():
    if not FALLBACK_DB:
        raise RuntimeError("Fallback DB deshabilitado")
    if psycopg is None:
        raise RuntimeError("psycopg no disponible")
    return psycopg.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD, autocommit=True
    )

def db_ensure_device(conn, imei: str, tenant_id: Optional[int]) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH up AS (
              INSERT INTO devices (name, external_id, tenant_id)
              VALUES (%s, %s, %s)
              ON CONFLICT (external_id) DO UPDATE SET name = EXCLUDED.name
              RETURNING id
            )
            SELECT id FROM up
            UNION ALL
            SELECT id FROM devices WHERE external_id = %s
            LIMIT 1
            """,
            (f"teltonika {imei}", imei, tenant_id, imei),
        )
        row = cur.fetchone()
        return int(row[0])

def db_insert_batch(conn, device_id: int, batch: List[Dict[str, Any]]):
    with conn.cursor() as cur:
        for r in batch:
            ts_ms = int(r.get("ts") or 0)
            cur.execute(
                "INSERT INTO telemetry (device_id, ts, data) "
                "VALUES (%s, to_timestamp(%s/1000.0), %s::jsonb)",
                (device_id, ts_ms, json.dumps(r)),
            )

# ----------------------------------------
# Protocolo Teltonika TCP
# ----------------------------------------
async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    log.info("Conexión %s", addr)

    try:
        # 1) IMEI handshake
        b_len = await reader.readexactly(2)
        imei_len = struct.unpack(">H", b_len)[0]
        imei = (await reader.readexactly(imei_len)).decode("ascii", "ignore").strip()
        log.info("IMEI=%s", imei)

        # ACK IMEI (01)
        writer.write(b"\x01")
        await writer.drain()

        # 2) Loop de paquetes AVL
        while True:
            # header: preamble(4) + data_length(4)
            header = await reader.readexactly(8)
            pre, data_len = struct.unpack(">II", header)
            if pre != 0:
                log.warning("Preamble inesperado: %08x", pre)
                # seguir leyendo hasta el próximo paquete
                continue

            data = await reader.readexactly(data_len)  # codec..records..n2
            _crc = await reader.readexactly(4)         # CRC (no validado)

            # ACK = n2 (último byte) en 4 bytes big-endian
            ack = data[-1] if data else 0
            writer.write(struct.pack(">I", ack))
            await writer.drain()

            # Armar payload para API
            payload: Dict[str, Any] = {"external_id": imei}
            headers = {}
            if DEFAULT_TENANT_ID:
                headers["X-Tenant-Id"] = DEFAULT_TENANT_ID  # mayúscula por convención

            # Decodificar tolerante; si falla, mandar raw
            try:
                codec, n2, records = decode_avl_data(data)
                payload["codec"] = codec
                payload["batch"] = records
                log.info("Paquete codec=0x%02x records=%d", codec, n2)
            except Exception as e:
                log.exception("Decode falló, envío raw: %s", e)
                payload["raw_hex"] = data.hex()

            # Enviar a API; fallback para cualquier estado >= 300 o error de red
            try:
                r = requests.post(INGEST_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
                if r.status_code >= 300:
                    log.error("API %s => %s %s", INGEST_URL, r.status_code, r.text)
                    if FALLBACK_DB:
                        try:
                            conn = db_get_conn()
                            try:
                                dev_id = db_ensure_device(
                                    conn, imei, int(DEFAULT_TENANT_ID) if DEFAULT_TENANT_ID else None
                                )
                                if "batch" in payload:
                                    db_insert_batch(conn, dev_id, payload["batch"])
                                else:
                                    db_insert_batch(conn, dev_id, [{"ts": 0, "raw_hex": payload["raw_hex"]}])
                                log.info("Fallback DB insertado IMEI=%s (device_id=%s)", imei, dev_id)
                            finally:
                                conn.close()
                        except Exception:
                            log.exception("Fallback DB falló")
            except Exception as e:
                log.exception("Error llamando API: %s", e)
                if FALLBACK_DB:
                    try:
                        conn = db_get_conn()
                        try:
                            dev_id = db_ensure_device(
                                conn, imei, int(DEFAULT_TENANT_ID) if DEFAULT_TENANT_ID else None
                            )
                            if "batch" in payload:
                                db_insert_batch(conn, dev_id, payload["batch"])
                            else:
                                db_insert_batch(conn, dev_id, [{"ts": 0, "raw_hex": payload.get("raw_hex", "")}])
                            log.info("Fallback DB (error de red) insertado IMEI=%s (device_id=%s)", imei, dev_id)
                        finally:
                            conn.close()
                    except Exception:
                        log.exception("Fallback DB también falló")

    except asyncio.IncompleteReadError:
        log.info("Cliente %s cerró conexión", addr)
    except Exception as e:
        log.exception("Error con %s: %s", addr, e)
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def main():
    server = await asyncio.start_server(handle_client, LISTEN_HOST, LISTEN_PORT)
    addrs = ", ".join(str(s.getsockname()) for s in server.sockets)
    log.info("Escuchando en %s", addrs)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
