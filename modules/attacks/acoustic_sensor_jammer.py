#!/usr/bin/env python3
# Acoustic attack on MEMS microphones or ultrasonic sensors

import time, argparse, numpy as np, sounddevice as sd, json, os
from datetime import datetime

LOG_FILE = "results/acoustic_jammer_logs.json"
MITRE_TTP = "T1496"

def log_event(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def jam(freq=20000, duration=10):
    fs = 44100
    t = np.arange(0, duration, 1/fs)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    print(f"[+] Emitting {freq}Hz acoustic jamming wave...")
    sd.play(wave, fs)
    sd.wait()

def main():
    parser = argparse.ArgumentParser(description="Acoustic Jamming Attack")
    parser.add_argument("--freq", type=int, default=20000, help="Jamming frequency (Hz)")
    parser.add_argument("--duration", type=int, default=10, help="Duration (seconds)")
    args = parser.parse_args()

    jam(args.freq, args.duration)
    log_event({
        "timestamp": datetime.utcnow().isoformat(),
        "frequency": args.freq,
        "duration": args.duration,
        "success": True,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
