#!/usr/bin/env python3
import argparse, os, time, csv, json
from scapy.all import *
from threading import Thread

# Argument parser
parser = argparse.ArgumentParser(description="Wi-Fi Passive Scanner")
parser.add_argument('--iface', default="wlan0mon", help="Monitor-mode interface")
parser.add_argument('--duration', type=int, default=30, help="Scan duration (seconds)")
parser.add_argument('--json-only', action='store_true', help="Output only JSON")
parser.add_argument('--csv-only', action='store_true', help="Output only CSV")
parser.add_argument('--full', action='store_true', help="Verbose output (RSSI, vendor, etc.)")
args = parser.parse_args()

iface = args.iface
duration = args.duration
output_folder = "results/wifi"
os.makedirs(output_folder, exist_ok=True)

found = {}

def channel_hop():
    channels = [1, 6, 11] + list(range(1, 14))
    while True:
        for ch in channels:
            os.system(f"iwconfig {iface} channel {ch} >/dev/null 2>&1")
            time.sleep(2)

def sniff_wifi(pkt):
    if pkt.haslayer(Dot11Beacon):
        bssid = pkt[Dot11].addr2
        ssid = pkt[Dot11Elt].info.decode(errors="ignore") if pkt[Dot11Elt].info else "<hidden>"
        stats = pkt[Dot11Beacon].network_stats()
        channel = stats.get("channel", "N/A")
        crypto = stats.get("crypto", ["N/A"])
        rssi = pkt.dBm_AntSignal if hasattr(pkt, "dBm_AntSignal") else "N/A"

        if bssid not in found:
            found[bssid] = {
                "BSSID": bssid,
                "SSID": ssid,
                "Channel": channel,
                "Crypto": ', '.join(crypto),
                "Signal": rssi
            }
            if args.full:
                print(f"[+] {bssid} | {ssid} | CH {channel} | ENC: {crypto} | RSSI: {rssi}")

def write_output():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    base = f"{output_folder}/wifi_scan_{timestamp}"

    if not args.csv_only:
        json_path = f"{base}.json"
        with open(json_path, "w") as f:
            json.dump(list(found.values()), f, indent=2)
        print(f"[+] JSON saved to: {json_path}")

    if not args.json_only:
        csv_path = f"{base}.csv"
        with open(csv_path, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["BSSID", "SSID", "Channel", "Crypto", "Signal"])
            writer.writeheader()
            writer.writerows(found.values())
        print(f"[+] CSV saved to: {csv_path}")

if __name__ == "__main__":
    print(f"[+] Scanning Wi-Fi on {iface} for {duration} seconds...")
    hopper = Thread(target=channel_hop)
    hopper.daemon = True
    hopper.start()

    sniff(iface=iface, prn=sniff_wifi, timeout=duration, monitor=True)
    write_output()
