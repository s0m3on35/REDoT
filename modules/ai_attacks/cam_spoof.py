# AI Camera Spoofing Module

import cv2
import os
import time
import threading
import base64
import datetime
from flask import Flask, render_template_string, Response, send_from_directory
from flask_socketio import SocketIO, emit

# Configuration
SNAPSHOT_DIR = "snapshots"
QR_IMAGE = "qr_overlay.png"
CAMERA_INDEX = 0  # Default camera index
STREAM_PORT = 5000

# Ensure snapshot dir exists
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# Generate dummy QR if missing
if not os.path.exists(QR_IMAGE):
    import qrcode
    qr = qrcode.make("RedOT Spoof Activated")
    qr.save(QR_IMAGE)

# Flask app for dashboard preview
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

frame_lock = threading.Lock()
current_frame = None

@app.route('/')
def index():
    return render_template_string("""
    <html><head><title>RedOT Cam Spoof Preview</title></head>
    <body style="background:#111;color:white">
    <h1>Live Cam Spoof (RedOT)</h1>
    <img id="stream" width="640">
    <script>
    const sock = new WebSocket("ws://" + location.host + "/ws");
    sock.onmessage = evt => {
        document.getElementById("stream").src = "data:image/jpeg;base64," + evt.data;
    };
    </script>
    </body></html>
    """)

@app.route('/cam_preview.html')
def cam_preview():
    return index()

@app.route('/snapshots/<path:filename>')
def snapshot_file(filename):
    return send_from_directory(SNAPSHOT_DIR, filename)

@socketio.on('connect', namespace='/ws')
def connect_cam():
    emit('status', {'message': 'Connected to Cam Feed'})

def capture_loop():
    global current_frame
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[!] Cannot access camera.")
        return

    overlay = cv2.imread(QR_IMAGE, cv2.IMREAD_UNCHANGED)
    overlay = cv2.resize(overlay, (150, 150))

    print("[*] Spoofing webcam with overlay and timestamp. Press Ctrl+C to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cv2.putText(frame, "RedOT Spoof Active", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)

        # Overlay QR code
        h, w, _ = overlay.shape
        frame[10:10+h, 10:10+w] = overlay[:, :, :3]

        # Save snapshot
        snap_path = os.path.join(SNAPSHOT_DIR, f"spoof_{timestamp}.jpg")
        cv2.imwrite(snap_path, frame)

        # Update current frame for stream
        with frame_lock:
            current_frame = frame.copy()

        time.sleep(3)

def streamer_thread():
    global current_frame
    while True:
        with frame_lock:
            if current_frame is not None:
                _, buffer = cv2.imencode('.jpg', current_frame)
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                socketio.emit('message', jpg_as_text, namespace='/ws')
        time.sleep(0.5)

if __name__ == "__main__":
    cam_thread = threading.Thread(target=capture_loop, daemon=True)
    stream_thread = threading.Thread(target=streamer_thread, daemon=True)

    cam_thread.start()
    stream_thread.start()
    print(f"[✓] WebSocket Dashboard live at http://localhost:{STREAM_PORT}/cam_preview.html")
    socketio.run(app, port=STREAM_PORT)
