#!/usr/bin/env python3

import smbus2
import time
import json
import argparse
from datetime import datetime

LOG_FILE = "results/i2c_firmware_rebooter_log.json"
MITRE_TTP = "T1542.004"

def log(entry):
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def i2c_reboot(bus_num, addr, reg=0x00, payload=0xFF):
    try:
        bus = smbus2.SMBus(bus_num)
        bus.write_byte_data(addr, reg, payload)
        bus.close()
        return True
    except Exception as e:
        return False

def main():
    parser = argparse.ArgumentParser(description="I2C Firmware Rebooter/Injector")
    parser.add_argument("--bus", type=int, default=1)
    parser.add_argument("--addr", type=lambda x: int(x,0), required=True)
    parser.add_argument("--reg", type=lambda x: int(x,0), default=0x00)
    parser.add_argument("--payload", type=lambda x: int(x,0), default=0xFF)
    args = parser.parse_args()

    success = i2c_reboot(args.bus, args.addr, args.reg, args.payload)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "bus": args.bus,
        "addr": hex(args.addr),
        "reg": hex(args.reg),
        "payload": hex(args.payload),
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
