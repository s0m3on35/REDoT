# modules/attacks/ota_firmware_injector.py

import os
import time
import json
import subprocess
import datetime
from scapy.all import sniff, wrpcap, Raw

AGENT_ID = "ota_injector"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "webgui/killchain.json"
PCAP_DIR = "reports"
EXTRACTED_FW_DIR = "reports/firmware_dumps"
WEBSOCKET_TRIGGER = "webgui/push_event.py"

os.makedirs(PCAP_DIR, exist_ok=True)
os.makedirs(EXTRACTED_FW_DIR, exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
pcap_file = os.path.join(PCAP_DIR, f"ota_sniff_{timestamp}.pcap")
firmware_file = os.path.join(PCAP_DIR, f"firmware_snippet_{timestamp}.bin")

def log(msg):
    print(f"[OTA] {msg}")

def push_alert():
    alert = {
        "agent": AGENT_ID,
        "alert": "OTA firmware interceptor triggered",
        "type": "firmware",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")
    try:
        subprocess.Popen(["python3", WEBSOCKET_TRIGGER, json.dumps(alert)])
    except:
        log("WebSocket trigger failed")

def append_killchain(step):
    entry = {
        "agent": AGENT_ID,
        "step": step,
        "timestamp": time.time()
    }
    with open(KILLCHAIN_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def extract_payload(payload_bytes):
    with open(firmware_file, "wb") as f:
        f.write(payload_bytes)
    log(f"Extracted firmware snippet saved: {firmware_file}")
    append_killchain("Firmware dump extracted")

    # Try binwalk extraction
    extract_dir = os.path.join(EXTRACTED_FW_DIR, f"fw_{timestamp}")
    os.makedirs(extract_dir, exist_ok=True)
    try:
        subprocess.run(["binwalk", "-e", "-C", extract_dir, firmware_file], check=True)
        log(f"Binwalk extraction complete to: {extract_dir}")
        append_killchain("Firmware analysis via binwalk")
    except subprocess.CalledProcessError:
        log("Binwalk extraction failed")

def packet_callback(pkt):
    if pkt.haslayer(Raw):
        payload = pkt[Raw].load
        if b"firmware" in payload.lower() or b"\x7fELF" in payload or b"squashfs" in payload.lower():
            log("Possible OTA payload detected")
            extract_payload(payload)
            push_alert()

def sniff_packets():
    log("Starting OTA firmware sniffing...")
    pkts = sniff(filter="ip", prn=packet_callback, timeout=20)
    wrpcap(pcap_file, pkts)
    log(f"Packets saved to: {pcap_file}")
    append_killchain("OTA stream sniffed")

def main():
    sniff_packets()

if __name__ == "__main__":
    main()
