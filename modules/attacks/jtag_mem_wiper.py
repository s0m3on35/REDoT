#!/usr/bin/env python3

import subprocess, argparse, json, os
from datetime import datetime

LOG_FILE = "results/jtag_mem_wipe_logs.json"
MITRE_TTP = "T1055.012"

def log_wipe(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            existing = json.load(f)
    else:
        existing = []
    existing.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

def wipe_memory(start_addr, length, pattern="00"):
    try:
        payload = pattern * (length // 2)
        with open("memwipe.hex", "w") as f:
            f.write(f":020000040000FA\n:{length:02X}{start_addr:04X}00{payload}\n:00000001FF")
        subprocess.run(["openocd", "-f", "interface.cfg", "-f", "target.cfg", "-c",
                        f"program memwipe.hex verify reset exit"], check=True)
        return True
    except Exception as e:
        print(f"[!] Wipe failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="JTAG Memory Wiper via OpenOCD")
    parser.add_argument("--start", required=True, help="Start memory address (hex)")
    parser.add_argument("--length", type=int, required=True, help="Bytes to wipe")
    parser.add_argument("--pattern", default="00", help="Hex pattern to write (default 00)")
    args = parser.parse_args()

    result = wipe_memory(int(args.start, 16), args.length, args.pattern)
    log_wipe({
        "timestamp": datetime.utcnow().isoformat(),
        "start_addr": args.start,
        "length": args.length,
        "pattern": args.pattern,
        "success": result,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
