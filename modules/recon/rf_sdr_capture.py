!/usr/bin/env python3
#

import os
import time
import json
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

# === CONFIGURATION ===
AGENT_ID = "rf_sdr_capture"
CAPTURE_DIR = "rf_captures"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "reports/killchain.json"
BLE_CORRELATION_FILE = "results/ble_rf_correlations.json"
FREQ = "433920000"
DURATION = 10
SAMPLE_RATE = 2048000

# === FILE PATHS ===
timestamp = int(time.time())
SUB_FILE = f"{CAPTURE_DIR}/capture_{timestamp}.sub"
WAV_FILE = f"{CAPTURE_DIR}/capture_{timestamp}.wav"
PCAP_FILE = f"{CAPTURE_DIR}/capture_{timestamp}.pcap"
COMPRESSED_FILE = f"{CAPTURE_DIR}/capture_{timestamp}.sub.gz"

# === CHAIN MODULES ===
ENTROPY_ANALYZER = "modules/analysis/entropy_analyzer.py"
SIGNAL_CLONER = "modules/wireless/rf_signal_cloner.py"
BLE_MATCHER = "modules/recon/ble_rf_matcher.py"
COMPRESSOR = "modules/recon/rf_compressor.py"
WATERFALL_PLOTTER = "modules/recon/rf_waterfall_plotter.py"

# === UTILITIES ===
def log(msg):
    print(f"[SDR] {msg}")

def ensure_dirs():
    Path(CAPTURE_DIR).mkdir(parents=True, exist_ok=True)
    Path("webgui").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(parents=True, exist_ok=True)
    Path("results").mkdir(parents=True, exist_ok=True)

def push_alert():
    alert = {
        "agent": AGENT_ID,
        "alert": "SDR RF capture in progress",
        "type": "recon",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def fingerprint_file(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
            sha256 = hashlib.sha256(data).hexdigest()
            size = len(data)
            return {"sha256": sha256, "size": size, "path": path}
    except:
        return {}

def log_killchain(freq):
    entry = {
        "agent": AGENT_ID,
        "technique": "RF Signal Capture → Entropy Analysis → Replay Prep",
        "frequency": freq,
        "artifacts": {
            "sub": SUB_FILE,
            "wav": WAV_FILE,
            "pcap": PCAP_FILE,
            "compressed": COMPRESSED_FILE
        },
        "fingerprints": {
            "sub": fingerprint_file(SUB_FILE),
            "pcap": fingerprint_file(PCAP_FILE)
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
    log("Capturing raw IQ samples via rtl_sdr...")
    subprocess.call([
        "rtl_sdr", SUB_FILE, "-f", FREQ, "-s", str(SAMPLE_RATE),
        "-n", str(SAMPLE_RATE * DURATION)
    ])
    log(f"→ Raw RF saved to {SUB_FILE}")

def convert_to_wav():
    log("Converting .sub to WAV format...")
    subprocess.call([
        "sox", "-r", str(SAMPLE_RATE), "-e", "unsigned-integer", "-b", "8", "-c", "1",
        SUB_FILE, WAV_FILE
    ])
    log(f"→ WAV saved to {WAV_FILE}")

def decode_with_rtl_433():
    log("Decoding with rtl_433 to PCAP...")
    with open(PCAP_FILE, "w") as f:
        subprocess.call([
            "rtl_433", "-r", SUB_FILE, "-F", "pcap"
        ], stdout=f)
    log(f"→ PCAP saved to {PCAP_FILE}")

def chain_entropy_analyzer():
    log("→ Launching Entropy Analyzer...")
    subprocess.call(["python3", ENTROPY_ANALYZER, "--input", SUB_FILE])

def chain_signal_cloner():
    log("→ Launching RF Signal Cloner...")
    subprocess.call(["python3", SIGNAL_CLONER, "--input", SUB_FILE])

def correlate_ble_devices():
    log("→ Running BLE ↔ RF correlation analysis...")
    subprocess.call(["python3", BLE_MATCHER, "--rf", SUB_FILE, "--window", "30"])

def compress_signal_file():
    log("Compressing RF file...")
    subprocess.call(["python3", COMPRESSOR, "--input", SUB_FILE, "--output", COMPRESSED_FILE])
    log(f"→ Compressed file saved: {COMPRESSED_FILE}")

def plot_waterfall():
    log("→ Generating waterfall plot...")
    subprocess.call(["python3", WATERFALL_PLOTTER, "--input", SUB_FILE])

# === MAIN ===
def main():
    ensure_dirs()
    push_alert()
    log("SDR capture initiated")

    capture_raw_signal()
    convert_to_wav()
    decode_with_rtl_433()
    compress_signal_file()
    chain_entropy_analyzer()
    chain_signal_cloner()
    correlate_ble_devices()
    plot_waterfall()
    log_killchain(FREQ)

    log("✔ Capture + full analysis chain completed.")

if __name__ == "__main__":
    main()
