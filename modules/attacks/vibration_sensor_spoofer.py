#!/usr/bin/env python3

import argparse
import time
import json
import os
from datetime import datetime
import RPi.GPIO as GPIO

LOG_FILE = "results/vibration_spoof_log.json"
MITRE_TTP = "T1111"

SPOOF_PIN = 22

def log(entry):
    os.makedirs("results", exist_ok=True)
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def pulse_pin(pin, count=10, delay=0.1):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    for _ in range(count):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(delay)
    GPIO.cleanup()

def main():
    parser = argparse.ArgumentParser(description="Vibration Sensor Spoofer")
    parser.add_argument("--count", type=int, default=10, help="Number of spoof pulses")
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args()

    pulse_pin(SPOOF_PIN, args.count, args.delay)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "count": args.count,
        "delay": args.delay,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
