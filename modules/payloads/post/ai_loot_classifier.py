#!/usr/bin/env python3
# ai_loot_classifier.py — REDOT Post-Ex Loot Classification

import os
import json
import re
from datetime import datetime
from difflib import SequenceMatcher

# Optional: If using LLM or external APIs, load keys here
USE_AI = False

LOOT_DIRS = ["loot/", "logs/jtag/", "logs/uart/"]
CLASSIFIED_OUTPUT = "loot/classified_loot.json"
TAGGED_DIR = "loot/tagged"
os.makedirs(TAGGED_DIR, exist_ok=True)

SIGNATURES = {
    "credentials": [r"password\s*=\s*\S+", r"login:\s*\S+", r"passwd", r"user(name)?\s*=\s*\S+"],
    "firmware": [r"\x7fELF", r"u-boot", r"kernel version", r"Linux version"],
    "config": [r"\[.*\]", r"<\?xml", r"option\s+\S+\s+\S+", r"set\s+\S+\s+\S+"],
    "network": [r"ip addr", r"ifconfig", r"route", r"gateway", r"host\s*=\s*"],
    "bootloader": [r"U-Boot", r"BootROM", r"loader", r"stage 1"],
    "commands": [r"sudo", r"apt-get", r"systemctl", r"bash", r"curl", r"wget"],
    "logs": [r"\d{4}-\d{2}-\d{2}", r"ERROR", r"WARNING", r"panic"],
    "exfil": [r"\.docx", r"\.xlsx", r"\.pdf", r"confidential", r"classified"]
}

def classify_file(content):
    tags = []
    for category, patterns in SIGNATURES.items():
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                tags.append(category)
                break
    return tags

def smart_tag_name(name):
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)

def process_loot():
    results = {}
    for base_dir in LOOT_DIRS:
        for root, _, files in os.walk(base_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "rb") as f:
                        content = f.read(204800).decode(errors="ignore")
                        tags = classify_file(content)
                        if USE_AI and not tags:
                            # Placeholder for LLM classification fallback
                            tags.append("ai-unknown")

                        if tags:
                            smart_name = smart_tag_name(fname)
                            tagged_path = os.path.join(TAGGED_DIR, smart_name)
                            with open(tagged_path, "w") as out_f:
                                out_f.write(content)

                            results[fpath] = {"tags": tags, "tagged_path": tagged_path}
                except Exception as e:
                    continue
    return results

def save_results(results):
    timestamp = datetime.utcnow().isoformat()
    result_obj = {
        "timestamp": timestamp,
        "classified": results
    }
    with open(CLASSIFIED_OUTPUT, "w") as f:
        json.dump(result_obj, f, indent=2)
    print(f"[✓] Classification complete. Results saved to {CLASSIFIED_OUTPUT}")

def main():
    print("=== REDOT AI Loot Classifier ===")
    results = process_loot()
    if results:
        save_results(results)
    else:
        print("[-] No loot matched known signatures.")

if __name__ == "__main__":
    main()
