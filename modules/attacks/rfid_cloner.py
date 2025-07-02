# modules/attacks/rfid_cloner.py

import argparse
import subprocess
import os
import json
from datetime import datetime

LOG_PATH = "results/rfid_clone_logs.json"
MITRE_TTP = "T1557.002"

def log_clone(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def run_proxmark_clone(interface, output_file):
    print("[+] Starting RFID sniff via Proxmark3...")
    try:
        result = subprocess.run([
            "proxmark3", interface,
            "-c", f"hf 14a snoop; hf 14a list; hf mf dump; save {output_file}"
        ], capture_output=True, text=True, timeout=60)
        print(result.stdout)
        return "proxmark3", True
    except Exception as e:
        print(f"[!] Proxmark3 failed: {e}")
        return "proxmark3", False

def run_flipper_clone(output_file):
    print("[+] Starting RFID sniff via Flipper...")
    try:
        result = subprocess.run([
            "flipper", "read", "rfid", "--out", output_file
        ], capture_output=True, text=True, timeout=30)
        print(result.stdout)
        return "flipper", True
    except Exception as e:
        print(f"[!] Flipper failed: {e}")
        return "flipper", False

def clone_rfid(interface, tool, output_file):
    if tool == "proxmark3":
        hw_used, success = run_proxmark_clone(interface, output_file)
    elif tool == "flipper":
        hw_used, success = run_flipper_clone(output_file)
    else:
        print(f"[!] Unsupported tool: {tool}")
        return

    log_clone({
        "timestamp": datetime.utcnow().isoformat(),
        "tool": hw_used,
        "interface": interface,
        "output_file": output_file,
        "success": success,
        "ttp": MITRE_TTP
    })

    if success:
        print(f"[✓] RFID clone saved to {output_file}")
    else:
        print(f"[!] RFID cloning failed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RFID Card Cloner (Proxmark3 / Flipper)")
    parser.add_argument("--tool", required=True, choices=["proxmark3", "flipper"], help="Hardware tool to use")
    parser.add_argument("--interface", default="ttyACM0", help="Device interface (e.g., ttyACM0 for Proxmark3)")
    parser.add_argument("--output", default="results/cloned_rfid.bin", help="Output file for cloned tag")
    args = parser.parse_args()

    clone_rfid(args.interface, args.tool, args.output)
