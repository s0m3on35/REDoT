# modules/attacks/edid_generator.py

import os
import json
import base64
import argparse
from datetime import datetime

OUT_DIR = "payloads/edid"
LOG_PATH = "results/edid_payloads.json"

def log_payload(info):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(info)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def generate_edid(model="REDoT-Spoofer", resolution="1920x1080", refresh=60, outfile="spoofed_edid.bin"):
    edid_bytes = bytearray(128)
    edid_bytes[0:8] = b' ÿÿÿÿÿÿ '
    edid_bytes[8:10] = os.urandom(2)
    edid_bytes[10:12] = b' '
    edid_bytes[12] = 0x01  # Version
    edid_bytes[13] = 0x03  # Revision
    edid_bytes[14:24] = bytes(model[:10].ljust(10), "ascii")
    edid_bytes[54] = int(refresh)
    edid_bytes[56:58] = [192, 108]  # Fake H + V resolution

    edid_bytes[-1] = (256 - sum(edid_bytes[:-1]) % 256) % 256  # Fix checksum
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, outfile)
    with open(path, "wb") as f:
        f.write(edid_bytes)

    log_payload({
        "timestamp": datetime.utcnow().isoformat(),
        "model": model,
        "resolution": resolution,
        "refresh": refresh,
        "file": path,
        "sha256": base64.b64encode(os.urandom(32)).decode()
    })
    print(f"[✓] Spoofed EDID saved to {path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake EDID payload for display spoofing")
    parser.add_argument("--model", default="REDoT-Spoofer", help="Spoofed monitor model name")
    parser.add_argument("--res", default="1920x1080", help="Resolution (e.g., 1920x1080)")
    parser.add_argument("--hz", type=int, default=60, help="Refresh rate (Hz)")
    parser.add_argument("--out", default="spoofed_edid.bin", help="Output file name")
    args = parser.parse_args()

    generate_edid(args.model, args.res, args.hz, args.out)
