# modules/simulation/replay_mode.py

import argparse
import time
import json
import os
from datetime import datetime

def replay_log(log_file, delay=1.0):
    if not os.path.exists(log_file):
        print(f"[!] Log file not found: {log_file}")
        return

    with open(log_file, "r") as f:
        entries = json.load(f)

    print(f"[✓] Replaying {len(entries)} events from {log_file}")
    for entry in entries:
        print(f"[→] {entry}")
        time.sleep(delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay Mode - Simulate prior attack sessions")
    parser.add_argument("--log", required=True, help="Path to JSON log (e.g., exploit_logs.json)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between entries (seconds)")
    args = parser.parse_args()

    replay_log(args.log, args.delay)
