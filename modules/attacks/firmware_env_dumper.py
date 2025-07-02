#!/usr/bin/env python3

import argparse
import os
import subprocess
import json
from datetime import datetime

LOG_FILE = "results/firmware_env_dumper_log.json"
MITRE_TTP = "T1542.004"

def log(entry):
    os.makedirs("results", exist_ok=True)
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def dump_env_uart(device):
    cmd = f"screen {device} 115200"
    os.system(cmd)

def dump_env_ssh(host, user, pw):
    cmd = f"sshpass -p {pw} ssh {user}@{host} fw_printenv"
    subprocess.run(cmd, shell=True)

def main():
    parser = argparse.ArgumentParser(description="Firmware Bootloader ENV Dumper")
    parser.add_argument("--method", required=True, choices=["uart", "ssh"])
    parser.add_argument("--device", help="UART device (e.g., /dev/ttyUSB0)")
    parser.add_argument("--host", help="SSH host")
    parser.add_argument("--user", help="SSH user")
    parser.add_argument("--pw", help="SSH password")
    args = parser.parse_args()

    if args.method == "uart" and args.device:
        dump_env_uart(args.device)
    elif args.method == "ssh" and args.host and args.user and args.pw:
        dump_env_ssh(args.host, args.user, args.pw)
    else:
        print("[-] Insufficient parameters.")

    log({
        "timestamp": datetime.utcnow().isoformat(),
        "method": args.method,
        "target": args.host or args.device,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
