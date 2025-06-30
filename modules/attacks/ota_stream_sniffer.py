# modules/sniffers/ota_stream_sniffer.py

import os
import time
import json
import base64
from scapy.all import sniff, Raw, UDP, TCP
from datetime import datetime

AGENT_ID = "ota_sniffer"
LOG_DIR = "reports"
PCAP_FILE = os.path.join(LOG_DIR, "ota_traffic_capture.pcap")
KILLCHAIN_FILE = os.path.join(LOG_DIR, "killchain.json")
ALERT_FILE = "webgui/alerts.json"
CHAIN_SCRIPT = "modules/attacks/ota_firmware_injector.py"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs("webgui", exist_ok=True)

keywords = [
    b"firmware", b"squashfs", b"upgrade", b"ota.bin", b"\x1f\x8b\x08",  # gzip
    b"ELF", b"JFFS2", b"mksquashfs", b"\x28\xb5\x2f\xfd",               # LZMA
]

def log(msg):
    ts = datetime.utcnow().isoformat()
    full = f"[{ts}] [OTA-SNIFFER] {msg}"
    print(full)
    with open(f"{LOG_DIR}/ota_sniffer.log", "a") as f:
        f.write(full + "\n")

def update_killchain(event):
    entry = {
        "agent": AGENT_ID,
        "event": event,
        "time": time.time()
    }
    with open(KILLCHAIN_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def push_alert(msg="OTA stream detected"):
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": AGENT_ID,
            "alert": msg,
            "type": "firmware",
            "timestamp": time.time()
        }) + "\n")

def analyze_payload(pkt):
    if Raw in pkt:
        payload = pkt[Raw].load
        for k in keywords:
            if k in payload:
                log(f"Firmware-related keyword found: {k}")
                with open(f"{LOG_DIR}/firmware_snippet.bin", "wb") as f:
                    f.write(payload)
                push_alert("OTA pattern found in traffic")
                update_killchain("OTA update stream intercepted")
                os.system(f"python3 {CHAIN_SCRIPT}")
                break

def sniff_ota_packets():
    log("Sniffing for OTA firmware streams...")
    sniff(
        iface="any",
        prn=analyze_payload,
        store=False,
        filter="tcp or udp",
        timeout=90
    )

if __name__ == "__main__":
    sniff_ota_packets()
