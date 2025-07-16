#!/usr/bin/env python3
##!/usr/bin/env python3
# Enhanced REDoT SDR RF Capture Module

import os
import time
import json
import subprocess
import base64
import hashlib
from datetime import datetime
from urllib.request import urlopen

AGENT_ID = "rf_sdr_capture"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "reports/killchain.json"
CAPTURE_DIR = "rf_captures"
BLE_DB_FILE = "results/ble_scan_results.json"
WATERFALL_PLOTTER = "modules/recon/rf_waterfall_plotter.py"
FREQ = "433920000"
DURATION = 10
timestamp = int(time.time())
SUB_FILE = f"{CAPTURE_DIR}/capture_{timestamp}.sub"
WAV_FILE = f"{CAPTURE_DIR}/capture_{timestamp}.wav"
PCAP_FILE = f"{CAPTURE_DIR}/capture_{timestamp}.pcap"
FP_FILE = f"{CAPTURE_DIR}/fingerprint_{timestamp}.json"

ENTROPY_ANALYZER = "modules/analysis/entropy_analyzer.py"
SIGNAL_CLONER = "modules/wireless/rf_signal_cloner.py"
COMPRESSOR = "modules/utils/rf_compressor.py"
BLE_CORRELATOR = "modules/utils/ble_rf_matcher.py"

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

def log_killchain():
    os.makedirs("reports", exist_ok=True)
    entry = {
        "agent": AGENT_ID,
        "technique": "RF Signal Capture â Entropy Analysis â BLE Correlation â Compression â Replay Prep",
        "frequency": FREQ,
        "artifacts": {
            "sub": SUB_FILE,
            "wav": WAV_FILE,
            "pcap": PCAP_FILE,
            "fingerprint": FP_FILE
        },
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
    log("Converting to WAV...")
    subprocess.call([
        "sox", "-r", "2048000", "-e", "unsigned-integer", "-b", "8", "-c", "1",
        SUB_FILE, WAV_FILE
    ])
    log(f"WAV file saved: {WAV_FILE}")

def decode_with_rtl_433():
    log("Decoding with rtl_433...")
    with open(PCAP_FILE, "w") as f:
        subprocess.call([
            "rtl_433", "-r", SUB_FILE, "-F", "pcap"
        ], stdout=f)
    log(f"PCAP saved: {PCAP_FILE}")

def fingerprint_signal():
    log("Generating RF fingerprint...")
    with open(SUB_FILE, "rb") as f:
        raw = f.read()
        fingerprint = {
            "hash_sha256": hashlib.sha256(raw).hexdigest(),
            "size": len(raw),
            "time": datetime.utcnow().isoformat() + "Z"
        }
        with open(FP_FILE, "w") as fp:
            json.dump(fingerprint, fp, indent=2)
        log(f"Fingerprint stored in {FP_FILE}")

def correlate_with_ble():
    log("Correlating RF capture with BLE telemetry...")
    subprocess.call(["python3", BLE_CORRELATOR, "--rf", SUB_FILE, "--ble", BLE_DB_FILE])

def compress_rf():
    log("Compressing RF signal for storage/transmission...")
    subprocess.call(["python3", COMPRESSOR, "--input", SUB_FILE])

def chain_entropy_analyzer():
    log("â Launching Entropy Analyzer...")
    subprocess.call(["python3", ENTROPY_ANALYZER, "--input", SUB_FILE])

def chain_signal_cloner():
    log("â Launching RF Signal Cloner...")
    subprocess.call(["python3", SIGNAL_CLONER, "--input", SUB_FILE])

def plot_waterfall():
    log("Generating waterfall plot...")
    subprocess.call(["python3", WATERFALL_PLOTTER, "--input", SUB_FILE])

def main():
    push_alert()
    log("SDR capture started")
    capture_raw_signal()
    convert_to_wav()
    decode_with_rtl_433()
    fingerprint_signal()
    correlate_with_ble()
    compress_rf()
    chain_entropy_analyzer()
    chain_signal_cloner()
    plot_waterfall()
    log_killchain()
    log("Capture + chain complete.")

if __name__ == "__main__":
    main()
