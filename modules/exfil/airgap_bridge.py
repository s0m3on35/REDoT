# modules/exfil/airgap_bridge.py

import argparse
import time
import base64
import json
import os
from datetime import datetime
import wave
import struct

LOG_PATH = "results/airgap_exfil_log.json"

def log_exfil(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def generate_audio_exfil(data, out_file):
    binary_data = base64.b64encode(data.encode()).decode()
    framerate = 44100
    frequency = 1000  # Hz
    duration = len(binary_data) * 0.05  # duration proportional to data size
    amplitude = 32767

    wavef = wave.open(out_file, 'w')
    wavef.setnchannels(1)
    wavef.setsampwidth(2)
    wavef.setframerate(framerate)

    for char in binary_data:
        for i in range(int(framerate * 0.05)):
            value = int(amplitude * (ord(char) % 2) * 0.5)
            packed_value = struct.pack('<h', value)
            wavef.writeframes(packed_value)
    wavef.close()

def airgap_exfil(data, method="audio", out_file="results/airgap_exfil.wav"):
    if method == "audio":
        generate_audio_exfil(data, out_file)
        print(f"[✓] Data exfiltrated via audio to {out_file}")
        log_exfil({
            "timestamp": datetime.utcnow().isoformat(),
            "method": "audio",
            "payload_size": len(data),
            "output": out_file
        })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Airgap Bridge - Data Exfiltration")
    parser.add_argument("--data", required=True, help="Data to exfiltrate")
    parser.add_argument("--method", default="audio", choices=["audio"])
    parser.add_argument("--out", default="results/airgap_exfil.wav", help="Output path")
    args = parser.parse_args()

    airgap_exfil(args.data, args.method, args.out)
