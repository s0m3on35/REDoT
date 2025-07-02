#!/usr/bin/env python3

import argparse
import json
import os
import time
from datetime import datetime

LOG_FILE = "results/lidar_jammer_log.json"
MITRE_TTP = "T1202"

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

def jam_lidar(interface="lidar0", mode="flood", duration=5):
    if mode == "flood":
        for _ in range(duration):
            os.system(f"lidar-jam --iface {interface} --flood")
            time.sleep(1)
    elif mode == "spoof":
        os.system(f"lidar-jam --iface {interface} --spoof")
    elif mode == "pulse":
        for _ in range(duration):
            os.system(f"lidar-jam --iface {interface} --pulse")
            time.sleep(0.5)

def main():
    parser = argparse.ArgumentParser(description="LIDAR Sensor Jammer")
    parser.add_argument("--iface", default="lidar0", help="LIDAR interface")
    parser.add_argument("--mode", choices=["flood", "spoof", "pulse"], default="flood")
    parser.add_argument("--duration", type=int, default=5)
    args = parser.parse_args()

    jam_lidar(args.iface, args.mode, args.duration)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "interface": args.iface,
        "mode": args.mode,
        "duration": args.duration,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
