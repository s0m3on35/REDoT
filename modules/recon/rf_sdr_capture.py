#!/usr/bin/env python3
# REDoT: Enhanced RF SDR Recon + Capture

import os
import sys
import time
import json
import uuid
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

AGENT_ID = "rf_sdr_capture"
CAPTURE_DIR = Path("rf_captures")
ALERT_FILE = Path("webgui/alerts.json")
KILLCHAIN_FILE = Path("reports/killchain.json")
STIX_EXPORT = Path("results/stix_rf_capture_bundle.json")
ENTROPY_ANALYZER = "modules/analysis/entropy_analyzer.py"
SIGNAL_CLONER = "modules/wireless/rf_signal_cloner.py"
SPECTROGRAM_OUTPUT = CAPTURE_DIR / "spectrogram.png"

# ========== CLI ARGUMENTS ==========
parser = argparse.ArgumentParser(description="RF SDR Signal Capture + Analysis")
parser.add_argument("--freq", type=str, default="433920000", help="Center frequency in Hz (default: 433920000)")
parser.add_argument("--duration", type=int, default=10, help="Duration in seconds (default: 10)")
parser.add_argument("--device", choices=["rtl", "hackrf"], default="rtl", help="Force device selection")
parser.add_argument("--websocket", action="store_true", help="Enable WebSocket alerting")
args = parser.parse_args()

timestamp = int(time.time())
uid = uuid.uuid4().hex[:8]
SUB_FILE = CAPTURE_DIR / f"capture_{timestamp}_{uid}.sub"
WAV_FILE = CAPTURE_DIR / f"capture_{timestamp}_{uid}.wav"
PCAP_FILE = CAPTURE_DIR / f"capture_{timestamp}_{uid}.pcap"

# ========== UTILS ==========
def log(msg):
    print(f"[RF] {msg}")

def push_alert():
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    alert = {
        "agent": AGENT_ID,
        "alert": "RF signal capture in progress",
        "type": "recon",
        "timestamp": time.time(),
        "uid": uid
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def log_killchain(freq):
    entry = {
        "agent": AGENT_ID,
        "technique": "RF Signal Capture → Entropy → Replay Prep",
        "frequency": freq,
        "artifacts": {
            "sub": str(SUB_FILE),
            "wav": str(WAV_FILE),
            "pcap": str(PCAP_FILE),
            "spectrogram": str(SPECTROGRAM_OUTPUT)
        },
        "uid": uid,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if KILLCHAIN_FILE.exists():
        with open(KILLCHAIN_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(KILLCHAIN_FILE, "w") as f:
        json.dump(data, f, indent=2)

def capture_signal():
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    if args.device == "hackrf":
        log("Using HackRF...")
        cmd = ["hackrf_transfer", "-r", str(SUB_FILE), "-f", args.freq, "-s", "2000000", "-n", str(2000000 * args.duration)]
    else:
        log("Using RTL-SDR...")
        cmd = ["rtl_sdr", str(SUB_FILE), "-f", args.freq, "-s", "2048000", "-n", str(2048000 * args.duration)]

    log("Capturing raw signal...")
    subprocess.run(cmd, check=True)
    log(f"Saved: {SUB_FILE}")

def convert_to_wav():
    log("Converting to WAV...")
    subprocess.run([
        "sox", "-r", "2048000", "-e", "unsigned-integer", "-b", "8", "-c", "1",
        str(SUB_FILE), str(WAV_FILE)
    ], check=True)
    log(f"Saved WAV: {WAV_FILE}")

def generate_spectrogram():
    log("Generating spectrogram...")
    subprocess.run([
        "sox", str(WAV_FILE), "-n", "spectrogram", "-o", str(SPECTROGRAM_OUTPUT)
    ], check=True)
    log(f"Saved spectrogram: {SPECTROGRAM_OUTPUT}")

def decode_to_pcap():
    log("Decoding to PCAP with rtl_433...")
    with open(PCAP_FILE, "wb") as out:
        subprocess.run(["rtl_433", "-r", str(SUB_FILE), "-F", "pcap"], stdout=out)
    log(f"Saved PCAP: {PCAP_FILE}")

def run_entropy_analysis():
    log("→ Running Entropy Analyzer...")
    subprocess.run(["python3", ENTROPY_ANALYZER, "--input", str(SUB_FILE)])

def run_signal_cloner():
    log("→ Running RF Signal Cloner...")
    subprocess.run(["python3", SIGNAL_CLONER, "--input", str(SUB_FILE)])

def generate_stix_export():
    from datetime import datetime
    bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": [
            {
                "type": "observed-data",
                "id": f"observed-data--{uuid.uuid4()}",
                "first_observed": datetime.utcnow().isoformat() + "Z",
                "last_observed": datetime.utcnow().isoformat() + "Z",
                "number_observed": 1,
                "objects": {
                    "0": {
                        "type": "file",
                        "name": f"RF Capture {uid}",
                        "hashes": {},
                        "extensions": {
                            "artifact": {
                                "url": str(SUB_FILE),
                                "mime_type": "application/octet-stream"
                            }
                        }
                    }
                }
            }
        ]
    }
    STIX_EXPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(STIX_EXPORT, "w") as f:
        json.dump(bundle, f, indent=2)
    log(f"STIX export saved: {STIX_EXPORT}")

# ========== MAIN ==========
def main():
    push_alert()
    capture_signal()
    convert_to_wav()
    generate_spectrogram()
    decode_to_pcap()
    run_entropy_analysis()
    run_signal_cloner()
    log_killchain(args.freq)
    generate_stix_export()
    log("✓ Full RF capture + analysis complete.")

if __name__ == "__main__":
    main()
