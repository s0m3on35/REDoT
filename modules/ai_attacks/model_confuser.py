#!/usr/bin/env python3
import cv2
import numpy as np
import threading
import time
import os
import json
from flask import Flask, Response, request, send_file
from subprocess import Popen

app = Flask(__name__)
os.makedirs("logs/model_confuser", exist_ok=True)

streaming = False
frame_lock = threading.Lock()
latest_frame = None
persistent_noise = None
noise_path = "logs/model_confuser/persistent_noise.npy"
agent_log_path = "logs/agents.json"
cam_spoof_triggered = False

def log_event(event):
    log = {
        "module": "model_confuser",
        "event": event,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists(agent_log_path):
        with open(agent_log_path, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []
    data.append(log)
    with open(agent_log_path, "w") as f:
        json.dump(data, f, indent=2)

def trigger_cam_spoof():
    global cam_spoof_triggered
    if not cam_spoof_triggered:
        cam_spoof_triggered = True
        Popen(["python3", "modules/ai_attacks/cam_spoof.py"])

def generate_frames():
    global latest_frame, persistent_noise
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return
    log_event("camera_access_granted")
    while streaming:
        ret, frame = cap.read()
        if not ret:
            continue
        if persistent_noise is None:
            noise = np.random.normal(0, 50, frame.shape).astype(np.uint8)
        else:
            noise = persistent_noise
        adv_frame = cv2.add(frame, noise)
        cv2.putText(adv_frame, "Adversarial Pattern Active", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        h, w, _ = adv_frame.shape
        cv2.rectangle(adv_frame, (int(w/3), int(h/3)), (int(2*w/3), int(2*h/3)), (0, 255, 0), 2)
        trigger_cam_spoof()
        with frame_lock:
            latest_frame = adv_frame.copy()
        time.sleep(0.03)
    cap.release()

def stream_video():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            _, buffer = cv2.imencode('.jpg', latest_frame)
            frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/model_confuser_feed')
def model_confuser_feed():
    return Response(stream_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control', methods=['POST'])
def control():
    global streaming, persistent_noise
    cmd = request.json.get("cmd")
    if cmd == "start":
        if not streaming:
            streaming = True
            t = threading.Thread(target=generate_frames)
            t.start()
            log_event("stream_started")
            return {"status": "stream started"}
        return {"status": "already streaming"}
    elif cmd == "stop":
        streaming = False
        log_event("stream_stopped")
        return {"status": "stream stopped"}
    elif cmd == "persist_noise":
        persistent_noise = np.random.normal(0, 50, (480, 640, 3)).astype(np.uint8)
        np.save(noise_path, persistent_noise)
        log_event("persistent_noise_saved")
        return {"status": "persistent noise applied"}
    elif cmd == "clear_noise":
        persistent_noise = None
        log_event("persistent_noise_cleared")
        return {"status": "noise cleared"}
    return {"status": "unknown command"}

@app.route('/snapshot')
def snapshot():
    global latest_frame
    with frame_lock:
        if latest_frame is not None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            path = f"logs/model_confuser/adversarial_{timestamp}.jpg"
            cv2.imwrite(path, latest_frame)
            log_event(f"snapshot_saved:{path}")
            return send_file(path, mimetype='image/jpeg')
    return "No frame", 404

@app.route('/')
def index():
    return f"""
    <html><body style="background:#000;color:white;text-align:center;">
    <h1>RedOT AI Model Confuser</h1>
    <img src="/model_confuser_feed" width="640"/><br><br>
    <button onclick="fetch('/control',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{cmd:'start'}})}})">Start</button>
    <button onclick="fetch('/control',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{cmd:'stop'}})}})">Stop</button>
    <button onclick="fetch('/control',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{cmd:'persist_noise'}})}})">Lock Noise</button>
    <button onclick="fetch('/control',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{cmd:'clear_noise'}})}})">Clear Noise</button>
    <button onclick="window.open('/snapshot','_blank')">Snapshot</button>
    </body></html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8789)
