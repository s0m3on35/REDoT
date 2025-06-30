import os
import time
import json
import subprocess
from datetime import datetime

AGENT_ID = "rf_sdr_capture"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "reports/killchain.json"
CAPTURE_DIR = "rf_captures"
PCAP_FILE = f"{CAPTURE_DIR}/capture_{int(time.time())}.pcap"
SUB_FILE = f"{CAPTURE_DIR}/capture_{int(time.time())}.sub"
WAV_FILE = f"{CAPTURE_DIR}/capture_{int(time.time())}.wav"
FREQ = "433920000"  # Default: 433.92 MHz
DURATION = 10       # seconds

def log(msg):
    print(f"[SDR] {msg}")

def push_alert():
    os.makedirs("webgui", exist_ok=True)
    alert = {
        "agent": AGENT_ID,
        "alert": "SDR RF capture in progress",
        "type": "recon",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def log_killchain(freq):
    os.makedirs("reports", exist_ok=True)
    entry = {
        "agent": AGENT_ID,
        "technique": "RF Signal Capture",
        "frequency": freq,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if os.path.exists(KILLCHAIN_FILE):
        with open(KILLCHAIN_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(KILLCHAIN_FILE, "w") as f:
        json.dump(data, f, indent=2)

def capture_raw_signal():
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    log("Capturing raw IQ samples...")
    subprocess.call([
        "rtl_sdr", SUB_FILE, "-f", FREQ, "-s", "2048000", "-n", str(2048000 * DURATION)
    ])
    log(f"Saved raw RF to {SUB_FILE}")

def convert_to_wav():
    log("Converting to WAV for audio-style analysis...")
    subprocess.call([
        "sox", "-r", "2048000", "-e", "unsigned-integer", "-b", "8", "-c", "1",
        SUB_FILE, WAV_FILE
    ])
    log(f"Saved to {WAV_FILE}")

def decode_with_rtl_433():
    log("Decoding with rtl_433...")
    with open(PCAP_FILE, "w") as f:
        subprocess.call([
            "rtl_433", "-r", SUB_FILE, "-F", "pcap"
        ], stdout=f)
    log(f"Saved decoded packets to {PCAP_FILE}")

def main():
    push_alert()
    log("Starting SDR-based RF capture")
    capture_raw_signal()
    convert_to_wav()
    decode_with_rtl_433()
    log_killchain(FREQ)
    log("Capture complete.")

if __name__ == "__main__":
    main()
