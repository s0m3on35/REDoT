#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from rtlsdr import RtlSdr
from scipy.signal import spectrogram
import json
import time
from datetime import datetime
from pathlib import Path

# Configuration
CENTER_FREQ = 2.437e9       # Wi-Fi Channel 6
SAMPLE_RATE = 2.4e6
GAIN = 'auto'
WINDOW_SIZE = 256
THRESHOLD = 1.5
STEP_SEC = 0.5
DURATION = 0                # 0 = infinite
SNAPSHOT_ON_MOTION = True   # Save PNG snapshot on motion detection

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True, parents=True)
LOG_FILE = RESULTS_DIR / "motion_log.json"
SNAPSHOT_DIR = RESULTS_DIR / "motion_screenshots"
SNAPSHOT_DIR.mkdir(exist_ok=True, parents=True)

def log_event(event: dict):
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")

def save_snapshot(fig, timestamp):
    filename = SNAPSHOT_DIR / f"motion_{timestamp.replace(':', '-')}.png"
    fig.savefig(filename, dpi=150)
    print(f"Snapshot saved: {filename}")

# Initialize SDR
sdr = RtlSdr()
sdr.sample_rate = SAMPLE_RATE
sdr.center_freq = CENTER_FREQ
sdr.gain = GAIN

# Initialize Plot
plt.ion()
fig, ax = plt.subplots(figsize=(12, 6))
banner = fig.add_axes([0.0, 0.92, 1.0, 0.05])  # Top banner

last_motion = False
start_time = time.time()

print("Starting Doppler motion detection with enhanced visualization")

try:
    while True:
        if DURATION and (time.time() - start_time > DURATION):
            break

        samples = sdr.read_samples(WINDOW_SIZE * 1024)
        f, t, Sxx = spectrogram(samples, fs=SAMPLE_RATE, nperseg=WINDOW_SIZE)
        power = 10 * np.log10(Sxx + 1e-10)
        band_mean = np.mean(power, axis=1)
        delta = np.ptp(band_mean)
        motion = delta > THRESHOLD

        timestamp = datetime.utcnow().isoformat() + "Z"

        if motion != last_motion:
            event_type = "motion_start" if motion else "motion_end"
            event = {
                "timestamp": timestamp,
                "event": event_type,
                "variance": round(float(delta), 2)
            }
            log_event(event)
            print(f"{event_type.upper()} at {timestamp} | Delta = {event['variance']:.2f} dB")
            last_motion = motion

            if motion and SNAPSHOT_ON_MOTION:
                save_snapshot(fig, timestamp)

        # Spectrogram Display
        ax.clear()
        pcm = ax.pcolormesh(t, f, power, shading='auto', cmap='plasma',
                            norm=LogNorm(vmin=1e-2, vmax=np.max(power)))
        ax.set_ylabel("Frequency (Hz)", fontsize=12)
        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_title(f"Delta = {delta:.2f} dB | {'MOTION DETECTED' if motion else 'No motion'}",
                     fontsize=14, color='red' if motion else 'green')
        fig.colorbar(pcm, ax=ax, label='Power (dB)', pad=0.02)

        # Top Alert Banner
        banner.clear()
        banner.set_xticks([])
        banner.set_yticks([])
        banner.set_facecolor('#440000' if motion else '#002200')
        banner.text(0.5, 0.5,
                    'MOTION DETECTED' if motion else 'No Motion',
                    ha='center', va='center',
                    fontsize=16, color='white', weight='bold')

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.pause(STEP_SEC)

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    sdr.close()
    plt.ioff()
    plt.close()
    print("Motion detection session ended")
