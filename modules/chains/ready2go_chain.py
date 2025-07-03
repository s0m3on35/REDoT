# modules/chains/ready2go_chain.py

import subprocess
import time
import yaml
import os
from utils.yaml_loader import load_yaml
from tools.readme_autoupdate import log_action

TARGETS_FILE = "config/targets.yaml"
PAYLOAD_OUT_DIR = "results/ready2go_payloads"

def run_scan_scripts():
    print("[*] Running Wi-Fi scan...")
    subprocess.run(["python3", "modules/recon/wifi_scan.py"])
    print("[*] Running BLE scan...")
    subprocess.run(["python3", "modules/recon/ble_scan.py"])
    print("[*] Running RF sniffer...")
    subprocess.run(["python3", "modules/recon/rf_sniffer.py"])

def load_screen_targets():
    if not os.path.exists(TARGETS_FILE):
        print("[-] targets.yaml not found.")
        return {}
    targets = load_yaml(TARGETS_FILE)
    return {
        name: props for name, props in targets.items()
        if 'screen' in props.get('tags', []) or 'display' in props.get('tags', [])
    }

def prompt_target_selection(screen_targets):
    print("\nDiscovered Targets with Screens:")
    for idx, (name, props) in enumerate(screen_targets.items()):
        print(f"[{idx}] {name} ({props.get('ip')} / {props.get('interface')})")
    try:
        choice = int(input("Select a screen to override by number: "))
        selected_name = list(screen_targets.keys())[choice]
        return selected_name, screen_targets[selected_name]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None, None

def prompt_custom_message():
    print("\nEnter your message or HTML to display on the screen:")
    return input("Payload> ")

def generate_payload_file(target_name, payload):
    os.makedirs(PAYLOAD_OUT_DIR, exist_ok=True)
    filename = f"{PAYLOAD_OUT_DIR}/{target_name.replace(' ', '_')}_ready2go.html"
    with open(filename, "w") as f:
        f.write(payload)
    return filename

def deploy_payload(target_props, payload_file):
    print(f"\n[*] Simulated payload deployment to {target_props.get('ip')}...")
    print(f"[*] Payload file: {payload_file}")
    time.sleep(1)
    print("[+] Screen override payload simulated as deployed.")

def run():
    print("\n[READY2GO FULL CHAIN: RECON TO SCREEN INJECTION]")
    run_scan_scripts()
    screen_targets = load_screen_targets()
    if not screen_targets:
        print("[-] No screen targets detected.")
        return
    target_name, target_props = prompt_target_selection(screen_targets)
    if not target_name:
        return
    payload = prompt_custom_message()
    payload_file = generate_payload_file(target_name, payload)
    deploy_payload(target_props, payload_file)
    log_action(f"ready2go_chain -> {target_name}")

if __name__ == "__main__":
    run()
