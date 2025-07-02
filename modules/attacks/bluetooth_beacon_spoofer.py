#!/usr/bin/env python3

import argparse
import os
import time
import json
from datetime import datetime
import subprocess

LOG_FILE = "results/bluetooth_beacon_spoof_log.json"
MITRE_TTP = "T1608.002"

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

def spoof_beacon(name="BeaconX", mac="AA:BB:CC:DD:EE:FF", interval=100):
    subprocess.call("hciconfig hci0 up", shell=True)
    subprocess.call("hciconfig hci0 leadv 3", shell=True)
    subprocess.call(f"hcitool -i hci0 cmd 0x08 0x0008 {mac.replace(':',' ')}", shell=True)
    subprocess.call(f"hcitool -i hci0 name '{name}'", shell=True)
    time.sleep(interval)
    subprocess.call("hciconfig hci0 noscan", shell=True)

def main():
    parser = argparse.ArgumentParser(description="BLE Beacon Spoofer")
    parser.add_argument("--name", default="SpoofBeacon")
    parser.add_argument("--mac", default="AA:BB:CC:DD:EE:FF")
    parser.add_argument("--interval", type=int, default=100)
    args = parser.parse_args()

    spoof_beacon(args.name, args.mac, args.interval)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "spoofed_name": args.name,
        "spoofed_mac": args.mac,
        "duration": args.interval,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
