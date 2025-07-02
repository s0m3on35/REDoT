# modules/firmware/firmware_dropper.py

import argparse
import os
import shutil
import json
from datetime import datetime

DROP_PATH = "payloads/firmware_drops"
LOG_PATH = "results/firmware_drop_log.json"

def log_drop(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def drop_firmware(firmware_path, target_device, chain_module=None):
    os.makedirs(DROP_PATH, exist_ok=True)
    fname = os.path.basename(firmware_path)
    dst = os.path.join(DROP_PATH, f"{target_device}_{fname}")
    shutil.copy(firmware_path, dst)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "target": target_device,
        "firmware": fname,
        "dropped_to": dst,
        "chain": chain_module if chain_module else "none"
    }

    log_drop(log_entry)
    print(f"[✓] Firmware dropped to: {dst}")
    if chain_module:
        print(f"[→] Chain to post-exploitation module: {chain_module}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Firmware Dropper Module")
    parser.add_argument("--firmware", required=True, help="Path to firmware file")
    parser.add_argument("--target", required=True, help="Target device identifier")
    parser.add_argument("--chain", help="Optional post-ex module to trigger after drop")
    args = parser.parse_args()

    drop_firmware(args.firmware, args.target, args.chain)
