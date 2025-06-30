#!/usr/bin/env python3
"""
dashboard_cam_spoof.py - Real Camera Spoof Module with Dashboard Integration
- Auto-overlay QR/image
- WebSocket-style remote control
- Stream preview
- Snapshot with timestamp
"""

import cv2
import threading
import time
import os
import json
import base64
from flask import Flask, Response, request, jsonify, send_file

app = Flask(__name__)

# Flags and shared state
streaming = False
frame_lock = threading.Lock()
latest_frame = None
snapshot_path = "logs/cam_spoof/spoofed_snapshot.jpg"
overlay_img_path = "assets/overlay_qr.png"
os.makedirs("logs/cam_spoof", exist_ok=True)
os.makedirs("assets", exist_ok=True)

# Optional overlay generator (can generate overlay_qr.png if missing)
if not os.path.isfile(overlay_img_path):
    import qrcode
    qr = qrcode.make("https://redot-control.local")
    qr.save(overlay_img_path)

def generate_frames():
    global latest_frame
    cap = cv2.VideoCapture(0)
    overlay = cv2.imread(overlay_img_path, cv2.IMREAD_UNCHANGED)

    if overlay is None:
        print("[-] Overlay image not found.")
        return

    if not cap.isOpened():
        print("[-] Cannot access webcam.")
        return

    print("[+] Starting camera spoof stream...")

    while streaming:
        ret, frame = cap.read()
        if not ret:
            continue

        # Overlay QR/image
        try:
            h, w = overlay.shape[:2]
            frame[10:10+h, 10:10+w] = overlay[:, :, :3]
        except:
            pass

        # Add text label
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"Spoofed {timestamp}", (10, frame.shape[0]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        # Save latest frame
        with frame_lock:
            latest_frame = frame.copy()

        time.sleep(0.03)

    cap.release()
    print("[*] Camera spoof stream stopped.")

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

@app.route('/cam_feed')
def cam_feed():
    return Response(stream_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control', methods=['POST'])
def control_stream():
    global streaming
    cmd = request.json.get("cmd")
    if cmd == "start":
        if not streaming:
            streaming = True
            t = threading.Thread(target=generate_frames)
            t.start()
            return jsonify({"status": "stream started"})
        return jsonify({"status": "already streaming"})
    elif cmd == "stop":
        streaming = False
        return jsonify({"status": "stream stopped"})
    return jsonify({"status": "unknown command"})

@app.route('/snapshot')
def snapshot():
    global latest_frame
    with frame_lock:
        if latest_frame is not None:
            cv2.imwrite(snapshot_path, latest_frame)
            return send_file(snapshot_path, mimetype='image/jpeg')
    return "No frame", 404

@app.route('/')
def index():
    html = f"""
    <html>
    <head><title>RedOT Cam Spoof Dashboard</title></head>
    <body style="background:#111; color:white; text-align:center;">
    <h1>RedOT Live Cam Spoof</h1>
    <img src="/cam_feed" width="640" /><br/><br/>
    <button onclick="fetch('/control', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{cmd:'start'}})}})">Start</button>
    <button onclick="fetch('/control', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{cmd:'stop'}})}})">Stop</button>
    <button onclick="window.open('/snapshot','_blank')">Snapshot</button>
    </body></html>
    """
    return html

if __name__ == "__main__":
    print("[*] Cam Spoof Dashboard running at http://0.0.0.0:8787")
    app.run(host="0.0.0.0", port=8787)
