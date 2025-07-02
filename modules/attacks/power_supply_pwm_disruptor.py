#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time, argparse, json, os
from datetime import datetime

LOG_FILE = "results/pwm_disruptor_logs.json"
MITRE_TTP = "T1496"

def log_disruption(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def disrupt_pwm(pin=18, freq=100):
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        pwm = GPIO.PWM(pin, freq)
        pwm.start(0)
        for dc in range(0, 101, 5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.05)
        pwm.ChangeFrequency(200)
        for dc in reversed(range(0, 101, 5)):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.05)
        pwm.stop()
        GPIO.cleanup()
        return True
    except Exception as e:
        print(f"[!] PWM disrupt failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="GPIO Power Supply PWM Disruptor")
    parser.add_argument("--pin", type=int, default=18, help="PWM pin (default: 18)")
    parser.add_argument("--freq", type=int, default=100, help="Base frequency")
    args = parser.parse_args()

    result = disrupt_pwm(args.pin, args.freq)
    log_disruption({
        "timestamp": datetime.utcnow().isoformat(),
        "pin": args.pin,
        "frequency": args.freq,
        "success": result,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
