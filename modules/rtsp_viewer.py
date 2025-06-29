#!/usr/bin/env python3
import cv2
import os
import json
import time
import numpy as np
from threading import Thread
from datetime import datetime
from imutils.video import FPS
from pathlib import Path

CONFIG_PATH = "loot/config/rtsp_config.json"
MODEL_PROTO = "loot/models/deploy.prototxt"
MODEL_WEIGHTS = "loot/models/mask_detector.caffemodel"
LOG_PATH = "loot/alerts/rtsp_alerts.log"
CLIP_DIR = "loot/clips"

os.makedirs("loot/config", exist_ok=True)
os.makedirs("loot/models", exist_ok=True)
os.makedirs("loot/alerts", exist_ok=True)
os.makedirs(CLIP_DIR, exist_ok=True)

# === AUTO DOWNLOAD MODEL ===
def download_model():
    import urllib.request
    prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
    weights_url = "https://github.com/chandrikadeb7/Face-Mask-Detection/raw/master/mask_detector.caffemodel"
    print("[*] Downloading Caffe model...")
    urllib.request.urlretrieve(prototxt_url, MODEL_PROTO)
    urllib.request.urlretrieve(weights_url, MODEL_WEIGHTS)

if not (os.path.exists(MODEL_PROTO) and os.path.exists(MODEL_WEIGHTS)):
    download_model()

# === LOAD CONFIG ===
def load_config():
    if not os.path.exists(CONFIG_PATH):
        sample_config = {
            "cameras": [
                {"name": "Front Gate", "ip": "192.168.1.100", "url": "rtsp://192.168.1.100/live"},
                {"name": "Backyard", "ip": "192.168.1.101", "url": "rtsp://192.168.1.101/live"}
            ]
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(sample_config, f, indent=4)
    with open(CONFIG_PATH) as f:
        return json.load(f)

# === MOTION DETECTOR ===
class MotionDetector:
    def __init__(self, min_area=500):
        self.prev = None
        self.min_area = min_area

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if self.prev is None:
            self.prev = gray
            return False
        frame_delta = cv2.absdiff(self.prev, gray)
        self.prev = gray
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            if cv2.contourArea(c) > self.min_area:
                return True
        return False

# === PROCESS STREAM ===
def process_stream(name, url):
    print(f"[*] Starting stream from {name} ({url})")
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"[!] Failed to open stream: {url}")
        return

    net = cv2.dnn.readNetFromCaffe(MODEL_PROTO, MODEL_WEIGHTS)
    motion = MotionDetector()
    fps = FPS().start()
    record = False
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"[!] Stream ended: {url}")
            break

        alert = motion.detect(frame)
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
        net.setInput(blob)
        detections = net.forward()

        mask_detected = False
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                label = f"Face {int(confidence * 100)}%"
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                cv2.putText(frame, label, (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
                mask_detected = True

        # Record alert
        if alert or mask_detected:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log = f"{timestamp} ALERT {name} Motion: {alert} Face: {mask_detected}"
            with open(LOG_PATH, 'a') as f:
                f.write(log + "\n")
            if not record:
                filename = os.path.join(CLIP_DIR, f"{name}_{timestamp}.avi")
                out = cv2.VideoWriter(filename, fourcc, 10.0, (w, h))
                record = True

        if record and out:
            out.write(frame)

        overlay = f"{name} | FPS: {fps.fps():.2f} | Motion: {alert} | Face: {mask_detected}"
        cv2.putText(frame, overlay, (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 255), 1)
        cv2.imshow(f"{name}", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        fps.update()

    fps.stop()
    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()

# === MENU ===
def main():
    print("\n[RTSP Viewer - REDoT Edition]")
    print("1) Auto-discover from loot/recon/rtsp_hosts.txt")
    print("2) Load from config (JSON)")
    print("3) Enter RTSP URL manually")
    choice = input("Select option: ")

    targets = []

    if choice == '1':
        path = "loot/recon/rtsp_hosts.txt"
        if os.path.exists(path):
            with open(path) as f:
                targets = [line.strip() for line in f if line.strip()]
        else:
            print("[!] No recon file found.")
            return

    elif choice == '2':
        cfg = load_config()
        targets = [cam["url"] for cam in cfg["cameras"]]

    elif choice == '3':
        url = input("Enter RTSP URL: ")
        targets = [url]

    else:
        print("[!] Invalid option")
        return

    for i, target in enumerate(targets):
        name = f"Stream_{i+1}"
        t = Thread(target=process_stream, args=(name, target))
        t.daemon = True
        t.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
