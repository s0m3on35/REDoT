#!/usr/bin/env python3
# tools/update_module_device_map.py

import os
import re
import yaml
from collections import defaultdict

MODULE_DIR = "modules"
README_FILE = "README.md"
YAML_OUT = "config/module_device_map.yaml"
OUTPUT_SECTION_TAG = "<!-- DEVICE-MAP-AUTO -->"

DEVICE_MAP = {
    "ble": "BLE Adapter",
    "bluetooth": "BLE Adapter",
    "wifi": "WLAN Adapter",
    "rf": "SDR",
    "zigbee": "Zigbee Interface",
    "nfc": "NFC Reader",
    "rfid": "RFID Reader",
    "uart": "UART Interface",
    "jtag": "JTAG Probe",
    "can": "CAN Interface",
    "dns": "DNS Resolver",
    "ota": "Firmware Image",
    "firmware": "Firmware Image",
    "led": "LED Sign",
    "display": "Screen Interface",
    "screen": "Screen Interface",
    "camera": "Camera Feed",
    "rtsp": "Camera Stream",
    "voice": "Smart Speaker",
    "speaker": "Smart Speaker",
    "loop": "IoT Network",
    "relay": "Relay Device",
    "dashboard": "Web Dashboard",
    "copilot": "AI Engine",
    "report": "Reporting Engine",
    "killchain": "Agent Logger",
    "implant": "Target System",
    "stealth": "Target System",
    "websocket": "Web Dashboard",
    "model": "ML Model",
    "image": "Camera Feed",
    "button": "Physical Button",
    "fan": "Environmental Actuator",
    "sensor": "Environmental Sensor",
    "alarm": "Alarm System",
    "projector": "AV Device",
    "usb": "USB Interface",
    "power": "Power Control",
    "i2c": "I2C Bus",
    "dmx": "DMX Controller",
    "edid": "Display Interface",
    "smart": "Smart Device",
    "bus": "CAN Interface",
    "badge": "Access Badge",
    "lock": "Electronic Lock"
}

def guess_device(module_name):
    name = module_name.lower()
    for keyword, device in DEVICE_MAP.items():
        if keyword in name:
            return device
    return "Generic Target"

def scan_modules():
    device_map = {}
    for root, _, files in os.walk(MODULE_DIR):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, MODULE_DIR)
                device = guess_device(file)
                device_map[rel_path] = device
    return dict(sorted(device_map.items()))

def generate_table(device_map):
    rows = ["| Module | Required Device |", "|--------|-----------------|"]
    for module, device in device_map.items():
        rows.append(f"| `{module}` | {device} |")
    return "\n".join(rows)

def update_readme(device_map):
    if not os.path.exists(README_FILE):
        print("[!] README.md not found.")
        return

    with open(README_FILE, "r") as f:
        content = f.read()

    table = generate_table(device_map)
    pattern = re.compile(rf"{OUTPUT_SECTION_TAG}.*?{OUTPUT_SECTION_TAG}", re.DOTALL)
    replacement = f"{OUTPUT_SECTION_TAG}\n{table}\n{OUTPUT_SECTION_TAG}"

    updated = pattern.sub(replacement, content) if pattern.search(content) else f"{content.strip()}\n\n{replacement}\n"
    
    with open(README_FILE, "w") as f:
        f.write(updated)
    
    print("[✓] README.md device table updated.")

def update_yaml(device_map):
    os.makedirs(os.path.dirname(YAML_OUT), exist_ok=True)
    with open(YAML_OUT, "w") as f:
        yaml.dump(device_map, f, sort_keys=True)
    print(f"[✓] Device map saved to {YAML_OUT}")

if __name__ == "__main__":
    print("[*] Scanning modules...")
    mapping = scan_modules()
    update_readme(mapping)
    update_yaml(mapping)
