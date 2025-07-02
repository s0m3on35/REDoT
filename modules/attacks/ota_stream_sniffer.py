# modules/sniffers/ota_stream_sniffer.py

import os
import time
import json
import base64
import hashlib
import subprocess
from scapy.all import sniff, Raw
from datetime import datetime

AGENT_ID = "ota_sniffer"
LOG_DIR = "reports"
PCAP_FILE = os.path.join(LOG_DIR, f"ota_capture_{int(time.time())}.pcap")
SNIPPET_FILE = os.path.join(LOG_DIR, f"firmware_snippet_{int(time.time())}.bin")
METADATA_FILE = os.path.join(LOG_DIR, f"firmware_metadata_{int(time.time())}.json")
KILLCHAIN_FILE = os.path.join(LOG_DIR, "killchain.json")
ALERT_FILE = "webgui/alerts.json"
WEBSOCKET_TRIGGER = "webgui/push_event.py"
CHAIN_SCRIPT = "modules/attacks/ota_firmware_injector.py"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs("webgui", exist_ok=True)

KEYWORDS = [
    b"firmware", b"squashfs", b"upgrade", b"ota.bin", b"\x1f\x8b\x08",  # gzip
    b"ELF", b"JFFS2", b"mksquashfs", b"\x28\xb5\x2f\xfd",               # LZMA
]

def log(msg):
    ts = datetime.utcnow().isoformat()
    line = f"[{ts}] [OTA-SNIFFER] {msg}"
    print(line)
    with open(os.path.join(LOG_DIR, "ota_sniffer.log"), "a") as f:
        f.write(line + "\n")

def push_alert(message):
    alert = {
        "agent": AGENT_ID,
        "alert": message,
        "type": "firmware",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")
    try:
        subprocess.Popen(["python3", WEBSOCKET_TRIGGER, json.dumps(alert)])
    except:
        pass

def update_killchain(event):
    entry = {
        "agent": AGENT_ID,
        "event": event,
        "time": time.time()
    }
    with open(KILLCHAIN_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def export_metadata(payload):
    meta = {
        "timestamp": datetime.utcnow().isoformat(),
        "size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "base64_preview": base64.b64encode(payload[:64]).decode()
    }
    with open(METADATA_FILE, "w") as f:
        json.dump(meta, f, indent=2)
    log(f"Metadata exported: {METADATA_FILE}")

def analyze_payload(pkt):
    if Raw in pkt:
        payload = pkt[Raw].load
        for k in KEYWORDS:
            if k in payload:
                log(f"Keyword matched: {k}")
                with open(SNIPPET_FILE, "wb") as f:
                    f.write(payload)
                export_metadata(payload)
                push_alert("OTA firmware pattern intercepted")
                update_killchain("OTA stream matched and dumped")
                os.system(f"python3 {CHAIN_SCRIPT}")
                break

def sniff_ota_packets():
    log("Sniffing for OTA payloads...")
    pkts = sniff(
        iface="any",
        prn=analyze_payload,
        store=True,
        filter="tcp or udp",
        timeout=90
    )
    from scapy.utils import wrpcap
    wrpcap(PCAP_FILE, pkts)
    log(f"PCAP saved to: {PCAP_FILE}")

if __name__ == "__main__":
    sniff_ota_packets()
