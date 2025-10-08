#!/usr/bin/env python3
import socket, struct, argparse, time

def build_codec8_packet(lat=-33.41, lon=-70.61, speed=18, sats=7, alt=650, angle=0):
    codec = 0x08
    records = 1
    ts_ms = int(time.time() * 1000)
    prio = 0

    ilon = int(lon * 10000000)
    ilat = int(lat * 10000000)
    ialt = int(alt) & 0xFFFF
    iangle = int(angle) & 0xFFFF
    ispeed = int(speed) & 0xFFFF
    isats = int(sats) & 0xFF

    body = bytearray()
    body += struct.pack(">B", codec)
    body += struct.pack(">B", records)

    # Record (Codec8)
    body += struct.pack(">q", ts_ms)     # timestamp ms
    body += struct.pack(">B", prio)      # priority
    body += struct.pack(">i", ilon)      # longitude
    body += struct.pack(">i", ilat)      # latitude
    body += struct.pack(">H", ialt)      # altitude (2 bytes)
    body += struct.pack(">H", iangle)    # angle
    body += struct.pack(">B", isats)     # satellites
    body += struct.pack(">H", ispeed)    # speed

    # IO vacío
    body += struct.pack(">B", 0)  # event id
    body += struct.pack(">B", 0)  # total n
    body += struct.pack(">B", 0)  # n1
    body += struct.pack(">B", 0)  # n2
    body += struct.pack(">B", 0)  # n4
    body += struct.pack(">B", 0)  # n8

    body += struct.pack(">B", records)  # records again
    crc = 0
    pkt = b"\x00\x00\x00\x00" + struct.pack(">I", len(body)) + body + struct.pack(">I", crc)
    return pkt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5027)
    ap.add_argument("--imei", default="356307042123456")
    ap.add_argument("--lat", type=float, default=-33.41)
    ap.add_argument("--lon", type=float, default=-70.61)
    ap.add_argument("--speed", type=float, default=18.5)
    ap.add_argument("--alt", type=float, default=650)
    ap.add_argument("--count", type=int, default=3)
    args = ap.parse_args()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.host, args.port))

    imei_bytes = args.imei.encode("ascii")
    s.sendall(struct.pack(">H", len(imei_bytes)) + imei_bytes)
    ok = s.recv(1)
    if ok != b"\x01":
        raise RuntimeError("Handshake IMEI no OK")

    for _ in range(args.count):
        pkt = build_codec8_packet(args.lat, args.lon, args.speed, 7, args.alt, 0)
        s.sendall(pkt)
        ack = s.recv(4)
        if len(ack) != 4:
            raise RuntimeError("ACK incompleto")
        recs = struct.unpack(">I", ack)[0]
        print("ACK:", recs)
        time.sleep(0.5)

    s.close()

if __name__ == "__main__":
    main()
