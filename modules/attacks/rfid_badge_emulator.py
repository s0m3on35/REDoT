#!/usr/bin/env python3
# modules/attacks/rfid_badge_emulator.py

import argparse, time, json, os
from datetime import datetime

LOG_FILE = "results/rfid_emulation_log.json"
MITRE_TTP = "T0850"

def log(code):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "emulated_code": code,
        "ttp": MITRE_TTP
    }
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f: data = json.load(f)
    else: data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f: json.dump(data, f, indent=2)

def emulate_badge(code, device):
    try:
        with open("/tmp/emulated.rfid", "w") as f:
            f.write(code)
        os.system(f"rfid-emulate -d {device} -f /tmp/emulated.rfid")
        log(code)
        print(f"[✓] Emulated RFID badge: {code}")
    except Exception as e:
        print(f"[!] RFID emulation failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Emulate RFID badge code")
    parser.add_argument("--code", required=True, help="Badge code to emulate")
    parser.add_argument("--device", default="/dev/rfid0", help="RFID device interface")
    args = parser.parse_args()
    emulate_badge(args.code, args.device)
