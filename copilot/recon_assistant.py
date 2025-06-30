#!/usr/bin/env python3
"""
recon_assistant.py - REDOT Copilot Recon Assistant
Auto-analyzes recon logs and provides GPT-style actionable next steps.
"""

import os
import time
import random
import json
from datetime import datetime

# Paths to known recon log files
LOG_DIR = "logs"
LOG_FILES = {
    "wifi_scan": os.path.join(LOG_DIR, "wifi_scan.log"),
    "ble_scan": os.path.join(LOG_DIR, "ble_scan.log"),
    "rf_sniffer": os.path.join(LOG_DIR, "rf_sniffer.log")
}

SUGGESTIONS = [
    {
        "condition": "wifi_scan",
        "action": "Run Evil Twin attack using `wifi_attack.py` on the highest signal SSID."
    },
    {
        "condition": "ble_scan",
        "action": "Use `ble_crasher.py` to flood detected BLE beacons for disruption."
    },
    {
        "condition": "rf_sniffer",
        "action": "Replay strongest signal using `rf_signal_cloner.py` or analyze waveform."
    }
]

DASHBOARD_EVENT_LOG = "logs/dashboard/events.log"

def parse_log(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def log_to_dashboard(event_type, content):
    os.makedirs(os.path.dirname(DASHBOARD_EVENT_LOG), exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "content": content
    }
    with open(DASHBOARD_EVENT_LOG, "a") as logf:
        logf.write(json.dumps(entry) + "\n")

def analyze_recon():
    detected_modules = []

    print("\n[*] Scanning recon logs...\n")
    for module, path in LOG_FILES.items():
        entries = parse_log(path)
        if entries:
            detected_modules.append(module)
            print(f"[+] {module}: {len(entries)} entries found.")
        else:
            print(f"[-] {module}: No data detected.")

    print("\n[✓] Recon Complete.\n")
    return detected_modules

def suggest_actions(modules):
    print(" Copilot Suggestions:\n")
    for s in SUGGESTIONS:
        if s["condition"] in modules:
            print(f" - {s['action']}")
            log_to_dashboard("suggestion", s['action'])

def main():
    print("=== REDOT Recon Assistant Online ===")
    time.sleep(1)

    detected = analyze_recon()
    time.sleep(1)

    suggest_actions(detected)

    print("\n[✓] Suggestions logged. Review the dashboard for updates.\n")

if __name__ == "__main__":
    main()
