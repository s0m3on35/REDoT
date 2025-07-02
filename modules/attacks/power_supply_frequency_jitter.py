#!/usr/bin/env python3

import argparse, time, os, json
from datetime import datetime

LOG_FILE = "results/power_jitter_logs.json"
MITRE_TTP = "T1496"

def log_attack(data):
    os.makedirs("results", exist_ok=True)
    existing = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            existing = json.load(f)
    existing.append(data)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

def jitter_loop(duration=10):
    end = time.time() + duration
    while time.time() < end:
        os.system("stress --cpu 1 --timeout 0.3")
        time.sleep(0.2)

def main():
    parser = argparse.ArgumentParser(description="Power Supply Jitter Attack")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds")
    args = parser.parse_args()

    jitter_loop(args.duration)
    log_attack({
        "timestamp": datetime.utcnow().isoformat(),
        "duration_sec": args.duration,
        "success": True,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
