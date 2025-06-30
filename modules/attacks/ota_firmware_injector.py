# modules/attacks/ota_firmware_injector.py

import os
import time
import json
import base64
from datetime import datetime
import websocket

AGENT_ID = "ota_injector"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "reports/killchain.json"
LOG_FILE = "reports/ota_firmware.log"
PAYLOAD_FILE = "reports/ota_firmware.bin"
CHAIN_SCRIPT_1 = "modules/firmware/firmware_poisoner.py"
CHAIN_SCRIPT_2 = "modules/report_builder.py"
WS_DASHBOARD_URI = "ws://localhost:8765"

os.makedirs("reports", exist_ok=True)
os.makedirs("webgui", exist_ok=True)

def log(msg):
    ts = datetime.utcnow().isoformat()
    full = f"[{ts}] [OTA] {msg}"
    print(full)
    with open(LOG_FILE, "a") as f:
        f.write(full + "\n")

def push_alert_websocket(message):
    try:
        ws = websocket.create_connection(WS_DASHBOARD_URI, timeout=3)
        ws.send(json.dumps({
            "agent": AGENT_ID,
            "alert": message,
            "type": "firmware",
            "timestamp": time.time()
        }))
        ws.close()
    except Exception as e:
        log(f"WebSocket alert failed: {e}")

def push_alert_file():
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": AGENT_ID,
            "alert": "OTA firmware interceptor triggered",
            "type": "firmware",
            "timestamp": time.time()
        }) + "\n")

def update_killchain(event):
    entry = {
        "agent": AGENT_ID,
        "event": event,
        "time": time.time()
    }
    try:
        with open(KILLCHAIN_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log(f"Killchain update failed: {e}")

def inject_firmware():
    payload = b"INJECTED_FIRMWARE_PAYLOAD" + os.urandom(32)
    with open(PAYLOAD_FILE, "wb") as f:
        f.write(payload)
    log("Payload written to reports/ota_firmware.bin")
    with open("reports/ota_firmware_payload_base64.txt", "w") as f:
        f.write(base64.b64encode(payload).decode())
    log("Base64 version saved for forensic export")

def auto_chain():
    log("Chaining to firmware poisoner and report builder...")
    os.system(f"python3 {CHAIN_SCRIPT_1}")
    time.sleep(1)
    os.system(f"python3 {CHAIN_SCRIPT_2}")

def main():
    log("Launching OTA firmware injector")
    push_alert_file()
    push_alert_websocket("OTA firmware interceptor activated")
    update_killchain("OTA firmware payload injected")
    inject_firmware()
    auto_chain()

if __name__ == "__main__":
    main()
