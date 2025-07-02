#!/usr/bin/env python3

import cv2
import numpy as np
import time
import argparse
from datetime import datetime
import json
import os

LOG_FILE = "results/pixel_inverter_log.json"
MITRE_TTP = "T1491.001"

def log(entry):
    os.makedirs("results", exist_ok=True)
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def invert_screen(duration):
    cap = cv2.VideoCapture(":0", cv2.CAP_V4L2)
    if not cap.isOpened():
        return False

    start = time.time()
    while time.time() - start < duration:
        ret, frame = cap.read()
        if not ret:
            break
        inverted = cv2.bitwise_not(frame)
        cv2.imshow("Screen Glitch", inverted)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return True

def main():
    parser = argparse.ArgumentParser(description="Live Screen Pixel Inverter")
    parser.add_argument("--duration", type=int, default=10)
    args = parser.parse_args()

    success = invert_screen(args.duration)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "duration": args.duration,
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
