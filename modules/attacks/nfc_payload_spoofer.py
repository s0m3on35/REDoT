#!/usr/bin/env python3

import argparse
import json
import os
import time
from datetime import datetime
import subprocess

LOG_FILE = "results/nfc_spoof_log.json"
MITRE_TTP = "T1200"

def log(entry):
    os.makedirs("results", exist_ok=True)
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def emit_nfc(payload):
    ndef_file = "/tmp/fake_ndef.txt"
    with open(ndef_file, "w") as f:
        f.write(payload)
    subprocess.run(["nfc-mfclassic", "W", "A", "mydump.mfd", ndef_file], check=False)

def main():
    parser = argparse.ArgumentParser(description="NFC Tag Payload Spoofer")
    parser.add_argument("--payload", required=True, help="Raw text/URI to encode in NFC tag")
    args = parser.parse_args()

    emit_nfc(args.payload)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "payload": args.payload,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
