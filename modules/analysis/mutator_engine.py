# modules/analysis/mutator_engine.py

import argparse
import os
import base64
import hashlib
import random
import string
import json
from datetime import datetime

LOG_PATH = "results/mutated_payloads.json"

def mutate_text_payload(payload):
    # Base64 encode + random wrapper
    encoded = base64.b64encode(payload.encode()).decode()
    wrapper = ''.join(random.choices(string.ascii_letters, k=8))
    return f"{wrapper}::{encoded}::{wrapper[::-1]}"

def mutate_binary_payload(filepath):
    with open(filepath, "rb") as f:
        content = bytearray(f.read())
    # Flip random bits
    for i in range(10):
        index = random.randint(0, len(content) - 1)
        content[index] ^= 0xFF
    mutated_path = f"{filepath}.mutated"
    with open(mutated_path, "wb") as f:
        f.write(content)
    return mutated_path

def log_mutation(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Payload Mutation Engine")
    parser.add_argument("--text", help="Plaintext payload to mutate")
    parser.add_argument("--binary", help="Binary file to mutate")
    args = parser.parse_args()

    if args.text:
        mutated = mutate_text_payload(args.text)
        print(f"[✓] Mutated text payload: {mutated}")
        log_mutation({
            "timestamp": datetime.utcnow().isoformat(),
            "original": args.text,
            "mutated": mutated,
            "type": "text"
        })

    if args.binary:
        mutated_path = mutate_binary_payload(args.binary)
        print(f"[✓] Mutated binary saved as: {mutated_path}")
        sha256 = hashlib.sha256(open(mutated_path, "rb").read()).hexdigest()
        log_mutation({
            "timestamp": datetime.utcnow().isoformat(),
            "original": args.binary,
            "mutated_path": mutated_path,
            "sha256": sha256,
            "type": "binary"
        })
