# modules/attacks/relay_attack_orchestrator.py

import time
import json
import os
import random
import subprocess
from datetime import datetime
from scapy.all import sniff, wrpcap, RadioTap, Dot11

AGENT_ID = "relay_attack"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "reports/killchain.json"
RECON_FILE = "recon/wifi_scan.json"
PCAP_EXPORT = "reports/relay_session.pcap"
CHAIN_SCRIPTS = {
    "mqtt": "modules/firmware/firmware_poisoner.py",
    "access_ctrl": "modules/iot/access_replay.py",
    "default": "implant_dropper.py"
}
RF_CAPTURE_DIR = "rf_captures"

def log(msg):
    print(f"[RELAY] {msg}")

def push_alert():
    os.makedirs("webgui", exist_ok=True)
    alert = {
        "agent": AGENT_ID,
        "alert": "Proximity relay spoof initiated",
        "type": "relay",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def log_killchain(target_mac):
    os.makedirs("reports", exist_ok=True)
    entry = {
        "agent": AGENT_ID,
        "technique": "Proximity Relay Spoofing",
        "target": target_mac,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if os.path.exists(KILLCHAIN_FILE):
        with open(KILLCHAIN_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(KILLCHAIN_FILE, "w") as f:
        json.dump(data, f, indent=2)

def export_rf_replay():
    os.makedirs(RF_CAPTURE_DIR, exist_ok=True)
    filename = f"{RF_CAPTURE_DIR}/relay_{int(time.time())}.sub"
    with open(filename, "wb") as f:
        f.write(os.urandom(512))  # Replace with real RF if captured
    log(f"RF replay signal saved to {filename}")
    return filename

def capture_relay_session():
    iface = "wlan0mon"
    log(f"Capturing session traffic on interface: {iface}")
    packets = sniff(iface=iface, timeout=10)
    wrpcap(PCAP_EXPORT, packets)
    log(f"Relay session pcap exported: {PCAP_EXPORT}")

def select_chain_script():
    if not os.path.exists(RECON_FILE):
        return CHAIN_SCRIPTS["default"]
    with open(RECON_FILE, "r") as f:
        recon = json.load(f)
    for ap in recon.get("access_points", []):
        ssid = ap.get("ssid", "").lower()
        if "mqtt" in ssid:
            return CHAIN_SCRIPTS["mqtt"]
        if "door" in ssid or "access" in ssid:
            return CHAIN_SCRIPTS["access_ctrl"]
    return CHAIN_SCRIPTS["default"]

def execute_chain(script):
    log(f"Executing chained script: {script}")
    subprocess.Popen(["python3", script])

def main():
    log("Starting BLE/UWB relay spoof...")
    push_alert()
    time.sleep(1)
    target_mac = f"00:11:22:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}"
    log(f"Target device simulated: {target_mac}")
    log("Initiating RF relay capture...")
    export_rf_replay()
    capture_relay_session()
    time.sleep(2)
    log("Replay of access signal triggered.")
    log_killchain(target_mac)
    chain_script = select_chain_script()
    execute_chain(chain_script)

if __name__ == "__main__":
    main()
