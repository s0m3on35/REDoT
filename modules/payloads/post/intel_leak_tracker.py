#!/usr/bin/env python3
# REDOT: intel_leak_tracker.py
# Tracks suspicious data leaks by monitoring outgoing connections and scanning sensitive files

import os
import time
import socket
import threading
import subprocess
import re
import logging
from collections import deque

LOG_DIR = "logs/intel_leak"
LOG_FILE = os.path.join(LOG_DIR, "leak_tracker.log")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(filename=LOG_FILE,
                    format='[%(asctime)s] %(message)s',
                    level=logging.INFO,
                    datefmt='%H:%M:%S')

# List of sensitive keywords or regex patterns to detect leaks in files or network payloads
SENSITIVE_PATTERNS = [
    r"password\s*=\s*['\"].+['\"]",
    r"api_key\s*=\s*['\"].+['\"]",
    r"secret\s*=\s*['\"].+['\"]",
    r"token\s*=\s*['\"].+['\"]",
    r"ssn\s*[:=]\s*\d{3}-\d{2}-\d{4}",
    r"credit\s*card\s*number\s*[:=]?\s*\d{13,16}",
    # Add your own patterns
]

# Paths to monitor for sensitive files (adjust as needed)
MONITORED_PATHS = [
    "/tmp",
    "/var/log",
    "/home",
    # Add other directories you want to monitor
]

# Number of last network connections to keep for analysis
MAX_RECENT_CONNECTIONS = 100

# Store recent outbound connections for anomaly detection
recent_connections = deque(maxlen=MAX_RECENT_CONNECTIONS)

def log(msg):
    logging.info(msg)
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def scan_file_for_secrets(filepath):
    """
    Scan a file for sensitive patterns.
    """
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        findings = []
        for pattern in SENSITIVE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                findings.extend(matches)
        if findings:
            log(f"[FILE_SCAN] Sensitive data detected in {filepath}: {findings}")
    except Exception as e:
        # Possibly binary or inaccessible file, ignore
        pass

def monitor_files_loop():
    """
    Periodically scan monitored directories for new or modified files containing sensitive info.
    """
    last_checked = {}
    while True:
        for base_path in MONITORED_PATHS:
            for root, _, files in os.walk(base_path):
                for fname in files:
                    path = os.path.join(root, fname)
                    try:
                        mtime = os.path.getmtime(path)
                        if path not in last_checked or mtime > last_checked[path]:
                            scan_file_for_secrets(path)
                            last_checked[path] = mtime
                    except Exception:
                        continue
        time.sleep(120)  # Scan every 2 minutes

def parse_netstat():
    """
    Parse current outbound connections using netstat command.
    """
    try:
        proc = subprocess.run(['netstat', '-tn'], capture_output=True, text=True)
        connections = []
        for line in proc.stdout.splitlines():
            if line.startswith('tcp'):
                parts = line.split()
                if len(parts) >= 5 and parts[5] == 'ESTABLISHED':
                    local = parts[3]
                    remote = parts[4]
                    connections.append((local, remote))
        return connections
    except Exception as e:
        return []

def monitor_network_loop():
    """
    Monitor outgoing connections and detect anomalous or suspicious endpoints.
    """
    while True:
        conns = parse_netstat()
        for conn in conns:
            if conn not in recent_connections:
                recent_connections.append(conn)
                # Basic suspicious check: remote IP not private network?
                remote_ip_port = conn[1]
                remote_ip = remote_ip_port.rsplit(':',1)[0]
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.connect((remote_ip, 80))
                    local_ip = sock.getsockname()[0]
                    sock.close()
                except Exception:
                    local_ip = None

                if remote_ip and not remote_ip.startswith("10.") and not remote_ip.startswith("192.168.") and not remote_ip.startswith("172."):
                    log(f"[NET_MONITOR] New outbound connection to public IP: {remote_ip_port}")
        time.sleep(60)  # Check every minute

def main():
    print("=== REDOT Intel Leak Tracker ===")
    threading.Thread(target=monitor_files_loop, daemon=True).start()
    threading.Thread(target=monitor_network_loop, daemon=True).start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
