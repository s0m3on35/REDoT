# modules/attacks/firmware_injection_verifier.py

import os
import argparse
import json
from hashlib import sha256
from datetime import datetime
import subprocess

LOG_PATH = "results/firmware_injection_verification.json"
KNOWN_SIGNATURE = b"<!-- PAYLOAD INJECTION -->"
MITRE_TTP = "T1608.002"  # Trusted Relationship: Compromise Software Dependencies and Development Tools

def log_verification(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def check_for_signature(firmware_path, signature=KNOWN_SIGNATURE):
    with open(firmware_path, "rb") as f:
        content = f.read()
    found = signature in content
    fw_hash = sha256(content).hexdigest()
    return found, fw_hash

def attempt_mount_check(device_path, mount_path="/mnt/firmware_verify"):
    os.makedirs(mount_path, exist_ok=True)
    try:
        subprocess.run(["mount", device_path, mount_path], check=True)
        for root, _, files in os.walk(mount_path):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "rb") as f:
                        data = f.read()
                        if KNOWN_SIGNATURE in data:
                            subprocess.run(["umount", mount_path])
                            return True, full_path
                except:
                    continue
        subprocess.run(["umount", mount_path])
    except:
        return False, None
    return False, None

def verify(firmware_path, is_device=False):
    print(f"[+] Starting firmware injection verification...")
    timestamp = datetime.utcnow().isoformat()

    if is_device:
        found, file_path = attempt_mount_check(firmware_path)
        result = {
            "timestamp": timestamp,
            "device_verified": firmware_path,
            "payload_detected": found,
            "file_containing_payload": file_path if found else "N/A",
            "ttp": MITRE_TTP
        }
    else:
        found, fw_hash = check_for_signature(firmware_path)
        result = {
            "timestamp": timestamp,
            "firmware_verified": firmware_path,
            "sha256": fw_hash,
            "payload_detected": found,
            "ttp": MITRE_TTP
        }

    log_verification(result)

    if found:
        print(f"[✓] Injection detected in: {firmware_path}")
    else:
        print(f"[!] No injection detected. Safe to proceed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Firmware Injection Auto-Verification Module")
    parser.add_argument("--target", required=True, help="Firmware file path or block device path")
    parser.add_argument("--device", action="store_true", help="Flag if the target is a mounted device (/dev/sdX)")

    args = parser.parse_args()
    verify(args.target, is_device=args.device)
