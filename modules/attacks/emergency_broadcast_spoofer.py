#!/usr/bin/env python3
# modules/attacks/emergency_broadcast_spoofer.py

import os
import time
import argparse
import subprocess

LOG = "results/emergency_spoof.log"
AUDIO_FILE = "payloads/emergency_alert.mp3"

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")
    print(msg)

def broadcast_audio(file):
    try:
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-volume", "100", file], check=True)
        log(f"Broadcasted emergency alert: {file}")
    except Exception as e:
        log(f"[ERROR] Audio playback failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof Emergency Broadcast over connected audio systems")
    parser.add_argument("--file", default=AUDIO_FILE, help="Alert audio file to broadcast")
    args = parser.parse_args()
    broadcast_audio(args.file)
