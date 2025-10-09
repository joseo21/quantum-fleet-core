#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import struct
import json
import os
import logging
from typing import Tuple, Dict, Any, List, Optional

import requests

try:
    import psycopg  # Fallback DB opcional
except Exception:
    psycopg = None

# -------------------------------------------------------------------
# Configuración
# -------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s:%(name)s:%(message)s")
log = logging.getLogger("teltonika-tcp")

API_BASE = os.getenv("API_BASE", "http://api:8000").rstrip("/")
INGEST_URL = f"{API_BASE}/ingest/teltonika/ingest"
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5.0"))

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "quantumfleet")
DB_USER = os.getenv("DB_USER", "quantum")
DB_PASSWORD = os.getenv("DB_PASSWORD", "quantum")

LISTEN_HOST = os.getenv("TCP_HOST", "0.0.0.0")
LISTEN_PORT = int(os.getenv("TCP_PORT", "5027"))

READ_TIMEOUT = float(os.getenv("READ_TIMEOUT", "15"))  # s

# -------------------------------------------------------------------
# Utilidades de lectura binaria
# -------------------------------------------------------------------
def _u8(buf: bytes, pos: int) -> Tuple[int, int]:
    return buf[pos], pos + 1

def _u16(buf: bytes, pos: int) -> Tuple[int, int]:
    return struct.unpack_from(">H", buf, pos)[0], pos + 2

def _u32(buf: bytes, pos: int) -> Tuple[int, int]:
    return struct.unpack_from(">I", buf, pos)[0], pos + 4

def _u64(buf: bytes, pos: int) -> Tuple[int, int]:
    return struct.unpack_from(">Q", buf, pos)[0], pos + 8

# CRC16/IBM (polinomio 0xA001, init 0x0000). Teltonika lo almacena en 4 bytes.
def crc16_ibm(data: bytes) -> int:
    crc = 0x0000
    for b in data:
        crc ^= b
        for _ in range(8):
            if (crc & 1) != 0:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

async def read_exact(reader: asyncio.StreamReader, n: int) -> bytes:
    return await asyncio.wait_for(reader.readexactly(n), timeout=READ_TIMEOUT)

# Re-sincroniza leyendo byte a byte hasta encontrar preámbulo 00000000 y luego lee len+payload
async def read_frame(reader: asyncio.StreamReader) -> Tuple[int, bytes]:
    zeros = 0
    discarded = 0
    # Busca 4 ceros consecutivos (preamble)
    while zeros < 4:
        b = await read_exact(reader, 1)
        if b == b"\x00":
            zeros += 1
        else:
            discarded += 1
            zeros = 0
            # no log con nivel WARNING para no ensuciar; deja DEBUG si se necesita
            # log.debug("Descartado byte: %s", b.hex())

    # Lee longitud (4 bytes big-endian)
    len_bytes = await read_exact(reader, 4)
    data_len = struct.unpack(">I", len_bytes)[0]

    if discarded and log.isEnabledFor(logging.DEBUG):
        log.debug("Re-sincronizado tras descartar %d bytes", discarded)

    if data_len < 0:
        raise ValueError("Longitud negativa no válida")
    if data_len == 0:
        return 0, b""

    payload = await read_exact(reader, data_len)
    return data_len, payload

# -------------------------------------------------------------------
# Decodificación tolerante de payload Codec8
# -------------------------------------------------------------------
def decode_avl_payload(payload: bytes) -> Tuple[int, int, List[Dict[str, Any]], bool]:
    """
    Devuelve: (codec, nrecords, records[], crc_ok)
    Tolerante a CRC ausente/truncado y a N2 != N1.
    """
    if len(payload) < 2:
        raise ValueError("AVL demasiado corto")

    codec = payload[0]
    n1 = payload[1]
    pos = 2

    records: List[Dict[str, Any]] = []

    for _ in range(n1):
        ts, pos = _u64(payload, pos)
        prio, pos = _u8(payload, pos)
        lng, pos = _u32(payload, pos)
        lat, pos = _u32(payload, pos)
        alt, pos = _u16(payload, pos)
        ang, pos = _u16(payload, pos)
        sats, pos = _u8(payload, pos)
        spd, pos = _u16(payload, pos)

        gps = {
            "lat": (lat if lat <= 0x7FFFFFFF else lat - 0x100000000) / 10_000_000.0,
            "lon": (lng if lng <= 0x7FFFFFFF else lng - 0x100000000) / 10_000_000.0,
            "alt": alt,
            "ang": ang,
            "sat": sats,
            "speed": float(spd),
        }

        event_id, pos = _u8(payload, pos)
        total_io, pos = _u8(payload, pos)

        io: Dict[str, Any] = {}

        c1, pos = _u8(payload, pos)
        for _i in range(c1):
            _id, pos = _u8(payload, pos)
            _val, pos = _u8(payload, pos)
            io[str(_id)] = _val

        c2, pos = _u8(payload, pos)
        for _i in range(c2):
            _id, pos = _u8(payload, pos)
            _val, pos = _u16(payload, pos)
            io[str(_id)] = _val

        c4, pos = _u8(payload, pos)
        for _i in range(c4):
            _id, pos = _u8(payload, pos)
            _val, pos = _u32(payload, pos)
            io[str(_id)] = _val

        c8, pos = _u8(payload, pos)
        for _i in range(c8):
            _id, pos = _u8(payload, pos)
            _val, pos = _u64(payload, pos)
            io[str(_id)] = _val

        records.append({
            "ts": ts,
            "event_id": event_id,
            "prio": prio,
            "gps": gps,
            "io": io,
        })

    # N2 tolerante
    if pos >= len(payload):
        n2 = n1
        crc_ok = False
        return codec, n1, records, crc_ok

    n2, pos = _u8(payload, pos)
    if n2 != n1 and log.isEnabledFor(logging.DEBUG):
        log.debug("n2 != n1 (%d != %d), continúo tolerante", n2, n1)

    # CRC opcional (4 bytes)
    if pos + 4 <= len(payload):
        crc_recv, pos = _u32(payload, pos)
        crc_calc = crc16_ibm(payload[:-4])
        crc_ok = ((crc_recv & 0xFFFF) == crc_calc)
    else:
        if log.isEnabledFor(logging.DEBUG):
            log.debug("CRC ausente o truncado")
        crc_ok = False

    return codec, n1, records, crc_ok

# -------------------------------------------------------------------
# Persistencia (API + fallback DB)
# -------------------------------------------------------------------
def api_ingest(imei: str, rec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    body = {
        "external_id": imei,
        "ts": rec["ts"],
        "gps": rec["gps"],
        "io": rec["io"],
        "event_id": rec.get("event_id", 0),
    }
    try:
        r = requests.post(INGEST_URL, json=body, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            return r.json()
        log.error("API %s => %s %s", INGEST_URL, r.status_code, r.text[:200])
    except Exception as e:
        log.error("Error llamando API: %s", e)
    return None

def db_get_conn():
    if psycopg is None:
        raise RuntimeError("psycopg no disponible en la imagen")
    return psycopg.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD, autocommit=True
    )

def db_ensure_device(conn, imei: str) -> int:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO devices (name, external_id)
            VALUES (%s, %s)
            ON CONFLICT (external_id) DO NOTHING;
        """, (f"FMC650 {imei}", imei))
        cur.execute("SELECT id FROM devices WHERE external_id=%s;", (imei,))
        row = cur.fetchone()
        if not row:
            raise RuntimeError("No se pudo obtener/crear device")
        return int(row[0])

def db_insert_telemetry(conn, device_id: int, rec: Dict[str, Any]):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO telemetry (device_id, ts, data)
            VALUES (%s, to_timestamp(%s/1000.0), %s::jsonb)
        """, (device_id, rec["ts"], json.dumps({
            "gps": rec["gps"], "io": rec["io"], "event_id": rec.get("event_id", 0)
        })))

# -------------------------------------------------------------------
# Servidor
# -------------------------------------------------------------------
async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    try:
        # Handshake IMEI
        imei_len_b = await read_exact(reader, 2)
        imei_len = struct.unpack(">H", imei_len_b)[0]
        imei_b = await read_exact(reader, imei_len)
        imei = imei_b.decode("ascii", errors="ignore")
        log.info("Conexión %s IMEI=%s", peer, imei)

        # ACK IMEI ok
        writer.write(b"\x01")
        await writer.drain()

        while True:
            data_len, payload = await read_frame(reader)

            if data_len == 0:
                # Keep-alive / frame vacío por diseño → ACK=0 y continuar sin warnings
                writer.write(struct.pack(">I", 0))
                await writer.drain()
                if log.isEnabledFor(logging.INFO):
                    log.info("Frame vacío (len=0): ACK=0, continuo…")
                continue

            n_saved = 0
            try:
                codec, n1, records, crc_ok = decode_avl_payload(payload)
                log.info("Paquete codec=0x%02X records=%d (crc_ok=%s)", codec, n1, crc_ok)

                for rec in records:
                    ok = api_ingest(imei, rec)
                    if ok is None:
                        try:
                            conn = db_get_conn()
                            try:
                                dev_id = db_ensure_device(conn, imei)
                                db_insert_telemetry(conn, dev_id, rec)
                                n_saved += 1
                                log.info("Fallback DB insertado IMEI=%s (device_id=%s)", imei, dev_id)
                            finally:
                                conn.close()
                        except Exception as db_e:
                            log.error("Fallback DB falló: %s", db_e)
                    else:
                        n_saved += 1

            except Exception as e:
                log.error("Decode falló: %s", e)
                writer.write(struct.pack(">I", 0))
                await writer.drain()
                continue

            writer.write(struct.pack(">I", n_saved))
            await writer.drain()

    except asyncio.IncompleteReadError:
        log.info("Cliente %s cerró conexión", peer)
    except Exception as e:
        log.exception("Error con %s: %s", peer, e)
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def main():
    server = await asyncio.start_server(handle_client, LISTEN_HOST, LISTEN_PORT)
    addr = ", ".join(str(sock.getsockname()) for sock in (server.sockets or []))
    log.info("Escuchando en (%s, %s)", LISTEN_HOST, LISTEN_PORT)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except Exception:
        pass
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
