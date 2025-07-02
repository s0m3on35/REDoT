#!/usr/bin/env python3

import argparse, os, time, json
from datetime import datetime

LOG_FILE = "results/ir_payloads.json"
MITRE_TTP = "T1200"

def log_ir(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def send_ir_command(remote, command):
    cmd = f"irsend SEND_ONCE {remote} {command}"
    return os.system(cmd) == 0

def main():
    parser = argparse.ArgumentParser(description="Infrared Payload Injector via LIRC")
    parser.add_argument("--remote", required=True, help="Remote config name (e.g., SAMSUNG)")
    parser.add_argument("--command", required=True, help="Command to send (e.g., POWER, VOLUP)")
    args = parser.parse_args()

    success = send_ir_command(args.remote, args.command)
    log_ir({
        "timestamp": datetime.utcnow().isoformat(),
        "remote": args.remote,
        "command": args.command,
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
