#!/usr/bin/env python3

import os, json, time, socket, subprocess, argparse
import threading, uuid
from websocket import create_connection

AGENT_ID = f"socks_pivotor_{uuid.uuid4().hex[:6]}"
ALERT_FILE = "webgui/alerts.json"
AGENTS_FILE = "webgui/agents.json"
PROXYCHAINS_CONF = "proxychains.conf"
WS_URL = "ws://127.0.0.1:8765"

def log(msg):
    print(f"[PIVOT] {msg}")

def push_alert():
    alert = {
        "agent": AGENT_ID,
        "alert": "SOCKS proxy pivot active",
        "type": "pivot",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")
    try:
        ws = create_connection(WS_URL)
        ws.send(json.dumps(alert))
        ws.close()
    except Exception:
        pass

def update_inventory(ip, port):
    os.makedirs("webgui", exist_ok=True)
    data = []
    if os.path.exists(AGENTS_FILE):
        with open(AGENTS_FILE) as f:
            data = json.load(f)
    agent_entry = {
        "id": AGENT_ID,
        "type": "pivot",
        "ip": ip,
        "port": port,
        "timestamp": time.time()
    }
    data.append(agent_entry)
    with open(AGENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def export_proxychains(ip, port):
    config = f"""strict_chain
proxy_dns 
[ProxyList]
socks5 {ip} {port}
"""
    with open(PROXYCHAINS_CONF, "w") as f:
        f.write(config)
    log(f"Exported to {PROXYCHAINS_CONF}")

def passive_listener(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", port))
    sock.listen(5)
    log(f"Passive SOCKS fallback listener on port {port}")
    while True:
        conn, _ = sock.accept()
        conn.close()

def start_socks(ip, port):
    log(f"Starting SOCKS5 proxy at {ip}:{port}")
    subprocess.Popen(["ssh", "-N", "-D", f"{port}", f"{ip}"])
    push_alert()
    update_inventory(ip, port)
    export_proxychains(ip, port)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", required=True, help="Target IP to route traffic through")
    parser.add_argument("--port", type=int, default=1080, help="SOCKS port")
    parser.add_argument("--passive", action="store_true", help="Enable passive relay fallback")
    args = parser.parse_args()

    if args.passive:
        threading.Thread(target=passive_listener, args=(args.port,), daemon=True).start()

    start_socks(args.ip, args.port)
    while True:
        time.sleep(5)

if __name__ == "__main__":
    main()
