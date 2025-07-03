#!/usr/bin/env python3
# tools/readme_autoupdate.py

import os
import re
import argparse
import yaml

CATEGORIES = {
    "recon": "### Recon",
    "wireless": "### Wireless Attacks",
    "firmware": "### Firmware Analysis and Exploits",
    "hardware": "### Hardware Interface Attacks",
    "ai": "### AI Deception and Adversarial Attacks",
    "payloads": "### Payloads and C2",
    "exploits": "### Advanced Exploits and Field Attacks",
    "dashboard": "### Dashboard and Copilot"
}

CATEGORY_KEYWORDS = {
    "recon": ["wifi_scan", "ble_scan", "rf_sniffer", "recon"],
    "wireless": ["wifi_", "ble_", "rf_", "signal", "jammer"],
    "firmware": ["firmware", "ota", "cve_", "unpack", "dump", "uart"],
    "hardware": ["uart", "jtag", "relay", "i2c", "spi"],
    "ai": ["spoof", "confuser", "voice"],
    "payloads": ["dns_c2", "implant", "stealth", "loop_bomb", "watering"],
    "exploits": ["rfid", "can_bus", "screen", "public", "sign", "hijack", "inject", "poison"],
    "dashboard": ["dashboard", "copilot", "report", "killchain", "viewer"]
}

def load_device_map(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f)

def find_category(script_name):
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in script_name:
                return cat
    return "exploits"

def extract_description(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("#") and "!" not in line:
                    return line.strip("# ").strip()
        return "No description found"
    except:
        return "No description found"

def insert_modules_into_readme(readme_path, modules, device_map):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    updated_sections = {}

    for cat in CATEGORIES.keys():
        updated_sections[cat] = []

    for path, description in modules.items():
        name = os.path.basename(path)
        category = find_category(name)
        device = device_map.get(name, "Unknown")
        entry = f"- `{name}` – {description} [Device: {device}]"
        updated_sections[category].append(entry)

    for cat, header in CATEGORIES.items():
        pattern = rf"{re.escape(header)}\n(?:- .*\n)*"
        new_block = header + "\n" + "\n".join(sorted(updated_sections[cat])) + "\n"
        content = re.sub(pattern, new_block, content, flags=re.MULTILINE)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

def scan_modules(modules_root):
    modules = {}
    for root, dirs, files in os.walk(modules_root):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                desc = extract_description(full_path)
                modules[full_path] = desc
    return modules

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-update README.md with module listings and device tags")
    parser.add_argument("--readme", default="README.md", help="Path to README.md")
    parser.add_argument("--modules", default="modules/", help="Root folder of modules")
    parser.add_argument("--device-map", default="config/device_map.yaml", help="YAML file mapping modules to devices")

    args = parser.parse_args()

    device_map = load_device_map(args.device_map)
    modules = scan_modules(args.modules)
    insert_modules_into_readme(args.readme, modules, device_map)

    print(f"[✓] README.md updated with {len(modules)} modules.")
