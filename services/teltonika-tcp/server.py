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

# Auditoría (opcional)
AUDIT_ENABLED = os.getenv("AUDIT_ENABLED", "0").lower() in ("1", "true", "yes", "on")
AUDIT_URL = f"{API_BASE}/audit/emit"
AUDIT_TIMEOUT = float(os.getenv("AUDIT_TIMEOUT", "3.0"))

# DB: preferimos POSTGRES_* (como hace tu compose)
DB_HOST = os.getenv("POSTGRES_HOST") or os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT") or os.getenv("DB_PORT") or "5432")
DB_NAME = os.getenv("POSTGRES_DB") or os.getenv("DB_NAME", "quantumfleet")
DB_USER = os.getenv("POSTGRES_USER") or os.getenv("DB_USER", "quantum")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD") or os.getenv("DB_PASSWORD")

TCP_HOST = os.getenv("TCP_HOST", os.getenv("LISTEN_HOST", "0.0.0.0"))
TCP_PORT = int(os.getenv("TCP_PORT", os.getenv("LISTEN_PORT", "5027")))

READ_TIMEOUT = float(os.getenv("READ_TIMEOUT", "15"))  # s
HEX_DUMP_DEBUG = os.getenv("HEX_DUMP_DEBUG", "0").lower() in ("1", "true", "yes", "on")

# -------------------------------------------------------------------
# IO 
# -------------------------------------------------------------------
IO_NAME_MAP = {
    239: "Ignition",
    240: "Movement",
    21: "GSM Signal",
    200: "Sleep Mode",
    71: "GNSS Status",
    182: "GNSS HDOP",
    66: "External Voltage",
    24: "Speed",
    205: "GSM Cell ID",
    67: "Battery Voltage",
    68: "Battery Current",
    199: "Trip Odometer",
    216: "Total Odometer",
    1: "Digital Input 1",
    9: "Analog Input 1",
    179: "Digital Output 1",
    219: "CCID Part1",
    220: "CCID Part2",
    221: "CCID Part3",
    2: "Digital Input 2",
    3: "Digital Input 3",
    10: "Analog Input 2",
    180: "Digital Output 2",
    72: "Dallas Temperature 1",
    73: "Dallas Temperature 2",
    74: "Dallas Temperature 3",
    75: "Dallas Temperature 4",
    62: "Dallas Temperature ID 1",
    63: "Dallas Temperature ID 2",
    64: "Dallas Temperature ID 3",
    65: "Dallas Temperature ID 4",
    78: "iButton",
    76: "Fuel Counter",
    10640: "Impulse counter frequency 1",
    10641: "Impulse counter RPM 1",
    483: "Impulse Counter 2",
    10642: "Impulse counter frequency 2",
    10643: "Impulse counter RPM 2",
    10911: "Impulse counter value 1",
    10912: "Impulse counter value 3",
    10913: "Impulse counter frequency 3",
    10914: "Impulse counter RPM 3",
    10915: "Impulse counter value 4",
    10916: "Impulse counter frequency 4",
    10917: "Impulse counter RPM 4",
    4: "Digital Input 4",
    50: "Digital Output 3",
    51: "Digital Output 4",
    11: "Analog Input 3",
    245: "Analog Input 4",
    70: "PCB Temperature",
    5: "Dallas Temperature ID 5",
    10487: "1Wire Humidity 1",
    10488: "1Wire Humidity 2",
    449: "Ignition On Counter",
    1161: "IMEI",
    1148: "Connectivity Quality",
    87: "Fuel Level",
    88: "Engine Speed",
    89: "Axle weight 1",
    90: "Axle weight 2",
    135: "Fuel Rate",
    10348: "Fuel level 2",
    12: "Program Number",
    13: "Module ID",
    14: "Engine Worktime",
    15: "Engine Worktime (Counted)",
    16: "Total Mileage (Counted)",
    17: "Fuel Consumed (counted)",
    18: "Fuel Rate",
    19: "AdBlue Level Percent",
    20: "AdBlue Level Liters",
    23: "Engine Load",
    25: "Engine Temperature",
    26: "Axle 1 Load",
    27: "Axle 2 Load",
    30: "Vehicle Speed",
    31: "Accelerator Pedal Position",
    33: "Fuel Consumed",
    34: "Fuel Level Liters",
    35: "Engine RPM",
    36: "Total Mileage",
    37: "Fuel Level Percent",
    141: "Battery Temperature",
    142: "Battery Level Percent",
    143: "Door Status",
    521: "Load Weight",
    250: "Trip",
    247: "Crash Detection",
    251: "Immobilizer",
    254: "Green Driving Value",
    249: "Jamming",
    10611: "RS232_COM1Data",
    10612: "RS232_COM2Data",
    191: "Vehicle Speed",
    192: "Odometer",
    193: "Trip Distance",
    194: "Timestamp",
    10683: "Temperature 1",
    10684: "Temperature 2",
    10685: "Temperature 3",
    10686: "Temperature 4",
    10687: "Status 1",
    10688: "Status 2",
    10691: "Alarm 1",
    10692: "Alarm 2",
    10695: "Input 1",
    10696: "Input 2",
    10697: "Input 3",
    10698: "Input 4",
    701: "BLE Temperature 1",
    702: "BLE Temperature 2",
    705: "BLE Battery 1",
    706: "BLE Battery 2",
    709: "BLE Humidity 1",
    710: "BLE Humidity 2"
}

# -------------------------------------------------------------------
# Utilidades
# -------------------------------------------------------------------
def _need(buf: bytes, pos: int, need: int, what: str) -> None:
    if pos + need > len(buf):
        raise ValueError(f"Payload truncado: {what} (pos={pos}, need={need}, len={len(buf)})")

def _u8(buf: bytes, pos: int) -> Tuple[int, int]:
    _need(buf, pos, 1, "u8")
    return buf[pos], pos + 1

def _u16(buf: bytes, pos: int) -> Tuple[int, int]:
    _need(buf, pos, 2, "u16")
    return struct.unpack_from(">H", buf, pos)[0], pos + 2

def _u32(buf: bytes, pos: int) -> Tuple[int, int]:
    _need(buf, pos, 4, "u32")
    return struct.unpack_from(">I", buf, pos)[0], pos + 4

def _i32(buf: bytes, pos: int) -> Tuple[int, int]:
    _need(buf, pos, 4, "i32")
    return struct.unpack_from(">i", buf, pos)[0], pos + 4

def _u64(buf: bytes, pos: int) -> Tuple[int, int]:
    _need(buf, pos, 8, "u64")
    return struct.unpack_from(">Q", buf, pos)[0], pos + 8

def _to_hex_be(value: int, byte_len: int) -> str:
    return value.to_bytes(byte_len, "big", signed=False).hex()

def _reverse_hex_bytes(hex_str: str) -> str:
    return "".join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def _ascii_from_hex(hex_str: str) -> str:
    try:
        return bytes.fromhex(hex_str).decode("ascii", errors="ignore")
    except Exception:
        return ""

def _set_named(io_out: dict, io_id: int, value):
    name = IO_NAME_MAP.get(io_id)
    if name:
        io_out[name] = value
    else:
        io_out[str(io_id)] = value

# CRC16/IBM (0xA001, init 0x0000)
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

# Lee 4x00 + LEN(4) + DATA(LEN) + CRC(4). Valida CRC16 sobre DATA (se comparan 16 bits bajos del CRC de 32 bits).
async def read_frame(reader: asyncio.StreamReader) -> Tuple[int, bytes]:
    # preámbulo
    preamble = await read_exact(reader, 4)
    if preamble != b"\x00\x00\x00\x00":
        # re-sync byte a byte
        buf = bytearray(preamble)
        while True:
            b = await read_exact(reader, 1)
            buf.pop(0); buf.append(b[0])
            if buf == b"\x00\x00\x00\x00":
                break
    # len
    len_bytes = await read_exact(reader, 4)
    data_len = struct.unpack(">I", len_bytes)[0]
    if data_len <= 0:
        return data_len, b""

    # data + crc
    payload = await read_exact(reader, data_len)
    crc_recv_b = await read_exact(reader, 4)
    crc_recv = struct.unpack(">I", crc_recv_b)[0]
    crc_calc = crc16_ibm(payload) & 0xFFFF
    crc_ok = ((crc_recv & 0xFFFF) == crc_calc)

    if not crc_ok:
        if log.isEnabledFor(logging.DEBUG):
            log.debug("CRC inválido (calc=0x%04X, recv=0x%04X) => ACK=0", crc_calc, crc_recv & 0xFFFF)
        return -1, payload  # señalamos CRC malo
    return data_len, payload

# -------------------------------------------------------------------
# Decodificación Teltonika AVL (Codec 08 / 8E)
# -------------------------------------------------------------------
def decode_avl_payload(payload: bytes) -> Tuple[int, int, List[Dict[str, Any]], bool]:
    """
    Retorna: codec, total_records (según cabecera), records_list, crc_ok_assumed(True si read_frame validó)
    """
    pos = 0
    codec, pos = _u8(payload, pos)
    if codec not in (0x08, 0x8E):
        raise ValueError(f"Codec no soportado: 0x{codec:02X}")

    n1, pos = _u8(payload, pos)
    records: List[Dict[str, Any]] = []

    for _ in range(n1):
        rec: Dict[str, Any] = {}
        ts_ms, pos = _u64(payload, pos)
        prio, pos = _u8(payload, pos)

        lon, pos = _i32(payload, pos)
        lat, pos = _i32(payload, pos)
        alt, pos = _u16(payload, pos)
        angle, pos = _u16(payload, pos)
        sats, pos = _u8(payload, pos)
        speed, pos = _u16(payload, pos)

        # Event ID + total IO: tamaños varían por codec
        if codec == 0x08:
            event_id, pos = _u8(payload, pos)
            total_io, pos = _u8(payload, pos)
        else:  # 0x8E
            event_id, pos = _u16(payload, pos)
            total_io, pos = _u16(payload, pos)

        io_by_size: Dict[int, Dict[int, int]] = {1: {}, 2: {}, 4: {}, 8: {}}
        xbytes_map: Dict[int, str] = {}
        # ---- Grupo 1 byte ----
        if codec == 0x08:
            c1, pos = _u8(payload, pos)
            for _k in range(c1):
                io_id, pos = _u8(payload, pos)   # ID = 1 byte en 0x08
                val,   pos = _u8(payload, pos)
                io_by_size[1][io_id] = val
        else:  # 0x8E
            c1, pos = _u16(payload, pos)
            for _k in range(c1):
                io_id, pos = _u16(payload, pos)  # ID = 2 bytes en 0x8E
                val,   pos = _u8(payload, pos)
                io_by_size[1][io_id] = val

        # ---- Grupo 2 bytes ----
        if codec == 0x08:
            c2, pos = _u8(payload, pos)
            for _k in range(c2):
                io_id, pos = _u8(payload, pos)
                val,   pos = _u16(payload, pos)
                io_by_size[2][io_id] = val
        else:
            c2, pos = _u16(payload, pos)
            for _k in range(c2):
                io_id, pos = _u16(payload, pos)
                val,   pos = _u16(payload, pos)
                io_by_size[2][io_id] = val

        # ---- Grupo 4 bytes ----
        if codec == 0x08:
            c4, pos = _u8(payload, pos)
            for _k in range(c4):
                io_id, pos = _u8(payload, pos)
                val,   pos = _u32(payload, pos)
                io_by_size[4][io_id] = val
        else:
            c4, pos = _u16(payload, pos)
            for _k in range(c4):
                io_id, pos = _u16(payload, pos)
                val,   pos = _u32(payload, pos)
                io_by_size[4][io_id] = val

        # ---- Grupo 8 bytes ----
        if codec == 0x08:
            c8, pos = _u8(payload, pos)
            for _k in range(c8):
                io_id, pos = _u8(payload, pos)
                val,   pos = _u64(payload, pos)
                io_by_size[8][io_id] = val
        else:
            c8, pos = _u16(payload, pos)
            for _k in range(c8):
                io_id, pos = _u16(payload, pos)
                val,   pos = _u64(payload, pos)
                io_by_size[8][io_id] = val

        # ---- Grupo X-bytes (sólo 8E, ya estaba OK) ----
        if codec == 0x8E:
            cx, pos = _u16(payload, pos)
            for _k in range(cx):
                io_id, pos = _u16(payload, pos)
                vlen,  pos = _u16(payload, pos)
                _need(payload, pos, vlen, f"xbytes({io_id})")
                raw = payload[pos : pos + vlen]
                pos += vlen
                xbytes_map[io_id] = raw.hex()

        # Construcción del record
        gps = {
            "lat": lat / 1e7,
            "lon": lon / 1e7,
            "sat": sats,
            "hdop": None,
            "speed": float(speed),
        }
        io: Dict[str, Any] = {}

        # Post-proceso: iButton (0x4E, 8 bytes)
        if 0x4E in io_by_size[8]:
            ib_val = io_by_size[8][0x4E]
            ib_hex = _to_hex_be(ib_val, 8).upper()
            if ib_val != 0:
                io["IButton"] = ib_hex
                io["IButton_Reverse"] = _reverse_hex_bytes(ib_hex).upper()
                io["IButton_Connected"] = True
            else:
                io["IButton"] = "0"
                io["IButton_Reverse"] = ""
                io["IButton_Connected"] = False

        # Post-proceso: ICCID (DB/DC/DD concatenadas como ASCII)
        iccid_parts = []
        for pid in (0xDB, 0xDC, 0xDD):
            if pid in xbytes_map:
                iccid_parts.append(_ascii_from_hex(xbytes_map[pid]))
        if iccid_parts:
            iccid_full = "".join(iccid_parts).strip("\x00")
            if iccid_full:
                io["CCID"] = iccid_full
                io["CCID Part1"] = _ascii_from_hex(xbytes_map.get(0xDB, ""))
                io["CCID Part2"] = _ascii_from_hex(xbytes_map.get(0xDC, ""))
                io["CCID Part3"] = _ascii_from_hex(xbytes_map.get(0xDD, ""))

        # Nombrado amigable para todos los grupos 1/2/4/8
        for size_group in (1, 2, 4, 8):
            for io_id, val in io_by_size[size_group].items():
                _set_named(io, io_id, val)

        # X-bytes restantes expuestos como hex
        for io_id, hex_val in xbytes_map.items():
            if io_id not in (0xDB, 0xDC, 0xDD):  # ya procesados
                _set_named(io, io_id, "0x" + hex_val)

        rec["ts"] = ts_ms / 1000.0
        rec["event_id"] = event_id
        rec["priority"] = prio
        rec["gps"] = gps
        rec["io"] = io
        rec["rejected_io"] = {}  # puedes usarlo para IDs que decidas ignorar

        records.append(rec)

    # N2 (debe coincidir con n1, según protocolo)
    n2, pos = _u8(payload, pos)
    if n2 != n1:
        log.debug("Aviso: n1=%d n2=%d (no coinciden)", n1, n2)

    return codec, n1, records, True

# -------------------------------------------------------------------
# Fallback DB
# -------------------------------------------------------------------
def db_insert_records(imei: str, records: List[Dict[str, Any]]) -> None:
    if psycopg is None:
        raise RuntimeError("psycopg no disponible")

    conn = psycopg.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, connect_timeout=3
    )
    with conn, conn.cursor() as cur:
        # Busca o crea device
        cur.execute("SELECT id FROM devices WHERE external_id=%s LIMIT 1", (imei,))
        row = cur.fetchone()
        if row:
            device_id = row[0]
        else:
            # crea con tenant del primero que exista (o 1)
            cur.execute("SELECT tenant_id FROM devices LIMIT 1")
            trow = cur.fetchone()
            tenant_id = trow[0] if trow else 1
            cur.execute(
                "INSERT INTO devices (tenant_id, name, external_id) VALUES (%s,%s,%s) RETURNING id",
                (tenant_id, f"Teltonika {imei}", imei),
            )
            device_id = cur.fetchone()[0]

        for rec in records:
            # t.data => jsonb con gps/io
            data = {"gps": rec["gps"], "io": rec["io"], "rejected_io": rec.get("rejected_io", {})}
            cur.execute(
                "INSERT INTO telemetry (device_id, ts, data) VALUES (%s, to_timestamp(%s), %s::jsonb)",
                (device_id, rec["ts"], json.dumps(data)),
            )

        log.info("Fallback DB insertado IMEI=%s (device_id=%s)", imei, device_id)

# -------------------------------------------------------------------
# Ingest a API
# -------------------------------------------------------------------
def api_ingest(imei: str, codec: int, records: List[Dict[str, Any]]) -> bool:
    try:
        payload = {"imei": imei, "codec": codec, "records": records}
        r = requests.post(INGEST_URL, json=payload, timeout=REQUEST_TIMEOUT)
        if r.status_code // 100 == 2:
            return True
        log.error("API ingest falló HTTP %s: %s", r.status_code, r.text[:200])
        return False
    except Exception as e:
        log.error("API ingest error: %s", e)
        return False

# -------------------------------------------------------------------
# Servidor TCP
# -------------------------------------------------------------------
async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    try:
        # Handshake IMEI: 2 bytes length + ascii IMEI
        raw_len = await read_exact(reader, 2)
        imei_len = struct.unpack(">H", raw_len)[0]
        imei_b = await read_exact(reader, imei_len)
        imei = imei_b.decode(errors="ignore")
        log.info("Conexión %s IMEI=%s", addr, imei)
        # responder 0x01
        writer.write(b"\x01")
        await writer.drain()

        while True:
            try:
                data_len, payload = await read_frame(reader)
            except asyncio.IncompleteReadError:
                break

            if data_len == 0:
                break  # keep-alive sin data
            if data_len < 0:
                # CRC malo → ACK 0
                writer.write((0).to_bytes(4, "big"))
                await writer.drain()
                if HEX_DUMP_DEBUG and payload:
                    log.debug("PAYLOAD HEX len=%d : %s", len(payload), payload[:256].hex())
                continue

            if HEX_DUMP_DEBUG:
                log.debug("PAYLOAD HEX len=%d : %s", len(payload), payload[:min(256, len(payload))].hex())

            try:
                codec, n1, records, _ = decode_avl_payload(payload)
                log.info("Paquete codec=0x%02X records=%d (crc_ok=True)", codec, n1)
            except Exception as e:
                log.error("Decode falló: %s", e)
                writer.write((0).to_bytes(4, "big"))
                await writer.drain()
                continue

            # Enviar a API; si falla, fallback DB
            ok = api_ingest(imei, codec, records)
            if not ok:
                try:
                    db_insert_records(imei, records)
                except Exception as e:
                    log.error("Fallback DB falló: %s", e)

            # ACK = cantidad de records
            writer.write((n1).to_bytes(4, "big"))
            await writer.drain()

    except Exception as e:
        log.debug("Cierre por error con %s: %s", addr, e)
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def main():
    server = await asyncio.start_server(handle_client, TCP_HOST, TCP_PORT)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    log.info("Escuchando en %s", addrs)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

