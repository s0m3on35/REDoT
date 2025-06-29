#!/usr/bin/env python3
import argparse, os, time, json, signal, sys
from scapy.all import *
from threading import Thread
from collections import defaultdict
from datetime import datetime
from rich.table import Table
from rich.console import Console

try:
    import gps
    GPS_ENABLED = True
except ImportError:
    GPS_ENABLED = False

DEFAULT_CONFIG = {
    "iface": "wlan0",
    "duration": 60,
    "gps": False,
    "full": False,
    "stealth": False,
    "graph": False,
    "ssid": None,
    "vendor": None,
    "mac_prefix": None,
    "interval": 0
}

parser = argparse.ArgumentParser(description="REDoT Wi-Fi Recon - Phase 3C (Stealth + Scheduling + Config)")
parser.add_argument('--config', help="Path to JSON config file")
parser.add_argument('--iface', help="Wireless interface")
parser.add_argument('--duration', type=int, help="Scan duration in seconds")
parser.add_argument('--gps', action='store_true', help="Enable GPS tagging")
parser.add_argument('--full', action='store_true', help="Enable dashboard")
parser.add_argument('--stealth', action='store_true', help="Enable silent mode (no output)")
parser.add_argument('--graph', action='store_true', help="Export Graphviz .dot")
parser.add_argument('--ssid', help="Filter: SSID")
parser.add_argument('--vendor', help="Filter: vendor")
parser.add_argument('--mac-prefix', help="Filter: MAC prefix")
parser.add_argument('--interval', type=int, help="Repeat scan every N seconds (0 = once)")
args = parser.parse_args()

config = DEFAULT_CONFIG.copy()
if args.config:
    try:
        with open(args.config) as f:
            user_cfg = json.load(f)
            config.update(user_cfg)
    except:
        print("[!] Failed to load config file.")

for key in config:
    if getattr(args, key, None) is not None:
        config[key] = getattr(args, key)

iface = config["iface"]
iface_mon = f"{iface}mon"
duration = config["duration"]
output_folder = "results/wifi"
os.makedirs(output_folder, exist_ok=True)

found = {}
ssid_graph = defaultdict(set)
console = Console()
gps_coords = {}
oui_db = {}

def gps_tracker():
    try:
        session = gps.gps(mode=gps.WATCH_ENABLE)
        while True:
            report = session.next()
            if report['class'] == 'TPV' and hasattr(report, 'lat') and hasattr(report, 'lon'):
                gps_coords['lat'] = report.lat
                gps_coords['lon'] = report.lon
    except Exception:
        pass

def channel_hop():
    channels = [1, 6, 11] + list(range(1, 14))
    while True:
        for ch in channels:
            os.system(f"iwconfig {iface_mon} channel {ch} >/dev/null 2>&1")
            time.sleep(2)

def sniff_wifi(pkt):
    if pkt.haslayer(Dot11Beacon):
        bssid = pkt[Dot11].addr2
        ssid = pkt[Dot11Elt].info.decode(errors="ignore") if pkt[Dot11Elt].info else "<hidden>"
        stats = pkt[Dot11Beacon].network_stats()
        channel = stats.get("channel", "N/A")
        crypto = stats.get("crypto", ["N/A"])
        rssi = pkt.dBm_AntSignal if hasattr(pkt, "dBm_AntSignal") else "N/A"
        mac_prefix = bssid.upper()[0:8]
        vendor = oui_db.get(mac_prefix, "Unknown")

        if config["ssid"] and config["ssid"].lower() not in ssid.lower():
            return
        if config["mac_prefix"] and not bssid.lower().startswith(config["mac_prefix"].lower()):
            return
        if config["vendor"] and config["vendor"].lower() not in vendor.lower():
            return

        if bssid not in found:
            entry = {
                "BSSID": bssid,
                "SSID": ssid,
                "Channel": channel,
                "Crypto": ', '.join(crypto),
                "Signal": rssi,
                "Vendor": vendor,
                "Timestamp": datetime.now().isoformat()
            }
            if config["gps"] and 'lat' in gps_coords:
                entry["Lat"] = gps_coords['lat']
                entry["Lon"] = gps_coords['lon']
            found[bssid] = entry
            ssid_graph[ssid].add(bssid)
            if config["full"] and not config["stealth"]:
                show_table()

def show_table():
    table = Table(title="REDoT Wi-Fi Recon - Phase 3C", show_lines=True)
    table.add_column("BSSID", style="cyan", no_wrap=True)
    table.add_column("SSID", style="green")
    table.add_column("Channel")
    table.add_column("Signal")
    table.add_column("Crypto")
    table.add_column("Vendor")
    table.add_column("Lat")
    table.add_column("Lon")
    for entry in found.values():
        table.add_row(
            entry.get("BSSID", ""),
            entry.get("SSID", ""),
            str(entry.get("Channel", "")),
            str(entry.get("Signal", "")),
            entry.get("Crypto", ""),
            entry.get("Vendor", ""),
            str(entry.get("Lat", "-")),
            str(entry.get("Lon", "-"))
        )
    console.clear()
    console.print(table)

def write_outputs():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    base = f"{output_folder}/wifi_scan_{timestamp}"
    json_path = f"{base}.json"
    dot_path = f"{base}.dot"
    with open(json_path, "w") as f:
        json.dump(list(found.values()), f, indent=2)
    if not config["stealth"]:
        print(f"[+] JSON saved: {json_path}")
    if config["graph"]:
        with open(dot_path, "w") as f:
            f.write("graph WiFi {\n")
            for ssid, bssids in ssid_graph.items():
                ssid_node = ssid if ssid else "<hidden>"
                f.write(f'  "{ssid_node}" [shape=box];\n')
                for bssid in bssids:
                    f.write(f'  "{ssid_node}" -- "{bssid}";\n')
            f.write("}\n")
        if not config["stealth"]:
            print(f"[+] Graphviz .dot saved: {dot_path}")

def load_oui():
    try:
        with open("oui.csv") as f:
            for line in f:
                if "," in line:
                    prefix, name = line.strip().split(",", 1)
                    oui_db[prefix.upper()] = name
    except:
        pass

def set_monitor_mode():
    os.system(f"ip link set {iface} down")
    os.system(f"iw dev {iface} set type monitor")
    os.system(f"ip link set {iface} up")
    os.system(f"ip link add {iface_mon} type monitor")
    os.system(f"ip link set {iface_mon} up")

def restore_interface():
    os.system(f"ip link set {iface_mon} down")
    os.system(f"iw dev {iface_mon} del")
    os.system(f"iw dev {iface} set type managed")
    os.system(f"ip link set {iface} up")

def signal_handler(sig, frame):
    restore_interface()
    sys.exit(0)

def run_scan():
    global found, ssid_graph
    found = {}
    ssid_graph = defaultdict(set)
    hopper = Thread(target=channel_hop)
    hopper.daemon = True
    hopper.start()
    sniff(iface=iface_mon, prn=sniff_wifi, timeout=duration, monitor=True)
    write_outputs()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    load_oui()
    set_monitor_mode()
    if config["gps"] and GPS_ENABLED:
        gps_thread = Thread(target=gps_tracker)
        gps_thread.daemon = True
        gps_thread.start()
    if config["interval"] > 0:
        while True:
            run_scan()
            if not config["stealth"]:
                print(f"[i] Sleeping {config['interval']}s before next scan...")
            time.sleep(config["interval"])
    else:
        run_scan()
    restore_interface()
