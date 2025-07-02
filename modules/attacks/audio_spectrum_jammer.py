#!/usr/bin/env python3

import argparse, os, json, time
import numpy as np
import sounddevice as sd
from datetime import datetime

LOG_FILE = "results/audio_jammer_log.json"
MITRE_TTP = "T1200"

def log_jam(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_tone(freq, duration, rate=44100):
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * freq * t)
    return tone

def play_tone(freq, duration):
    tone = generate_tone(freq, duration)
    sd.play(tone, samplerate=44100)
    sd.wait()

def main():
    parser = argparse.ArgumentParser(description="Audio Spectrum Jammer")
    parser.add_argument("--freq", type=int, default=20000, help="Frequency in Hz")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds")
    args = parser.parse_args()

    play_tone(args.freq, args.duration)
    log_jam({
        "timestamp": datetime.utcnow().isoformat(),
        "frequency": args.freq,
        "duration": args.duration,
        "success": True,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
