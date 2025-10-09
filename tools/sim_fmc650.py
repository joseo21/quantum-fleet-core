#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, socket, struct, time

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

def build_record(ts_ms, lat, lon, speed_kmh):
    # Codec8 simple con 1 record y sin IO (solo contadores 0)
    # ts(8) prio(1)=0 lng(4) lat(4) alt(2)=650 ang(2)=0 sats(1)=7 speed(2)
    lat_i = int(round(lat  * 10_000_000))
    lon_i = int(round(lon  * 10_000_000))
    if lat_i < 0: lat_i += 1 << 32
    if lon_i < 0: lon_i += 1 << 32
    speed = int(round(speed_kmh))
    rec = struct.pack(">Q", ts_ms)                # ts
    rec += b"\x00"                                # prio
    rec += struct.pack(">I", lon_i)               # lng
    rec += struct.pack(">I", lat_i)               # lat
    rec += struct.pack(">H", 650)                 # alt
    rec += struct.pack(">H", 0)                   # ang
    rec += b"\x07"                                # sats
    rec += struct.pack(">H", speed)               # speed
    rec += b"\x00"                                # event_id
    rec += b"\x00"                                # total_io
    rec += b"\x00"                                # cnt 1B
    rec += b"\x00"                                # cnt 2B
    rec += b"\x00"                                # cnt 4B
    rec += b"\x00"                                # cnt 8B
    return rec

def build_avl_frame(ts_ms, lat, lon, speed_kmh):
    record = build_record(ts_ms, lat, lon, speed_kmh)
    payload = b"\x08"          # codec
    payload += b"\x01"         # N1=1
    payload += record
    payload += b"\x01"         # N2=1
    # CRC (4 bytes, pero Teltonika usa CRC16 en lower 16 bits)
    crc = crc16_ibm(payload)
    payload += struct.pack(">I", crc)  # 4 bytes

    # Header: 00000000 + len(payload)
    header = b"\x00\x00\x00\x00" + struct.pack(">I", len(payload))
    return header + payload

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--imei", required=True)
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--speed", type=float, default=0.0)
    ap.add_argument("--count", type=int, default=1)
    args = ap.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        imei_b = args.imei.encode("ascii")
        s.sendall(struct.pack(">H", len(imei_b)) + imei_b)
        ack = s.recv(1)
        if ack != b"\x01":
            raise RuntimeError("IMEI no aceptado")

        for i in range(args.count):
            ts_ms = int(time.time() * 1000)
            frame = build_avl_frame(ts_ms, args.lat, args.lon, args.speed)
            s.sendall(frame)
            ack4 = s.recv(4)
            if len(ack4) != 4:
                raise RuntimeError("ACK incompleto")
            n = struct.unpack(">I", ack4)[0]
            print(f"ACK: {n}")

if __name__ == "__main__":
    main()
