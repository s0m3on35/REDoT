#!/usr/bin/env python3


import asyncio
import argparse
import logging
import time
import csv
import json
import os
import sys
import importlib
import glob
import urllib.request
import socket
import requests
from datetime import datetime
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../../logs/ble_scan")
EXPLOITS_DIR = os.path.join(BASE_DIR, "exploits")
DASHBOARD_API = "http://localhost:5050/api/upload_ble_results"
GITHUB_EXPLOITS_RAW_BASE = "https://raw.githubusercontent.com/s0m3on35/REDoT/main/modules/recon/exploits"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(EXPLOITS_DIR, exist_ok=True)

def setup_logger(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%H:%M:%S'
    )

def log(msg):
    print(msg)
    logging.info(msg)

def download_file(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        log(f"[Update] Downloaded {url} to {dest}")
        return True
    except Exception as e:
        log(f"[Update] Failed to download {url}: {e}")
        return False

def update_exploits():
    exploit_files = [
        "ti_sensortag_dos.py",
        "nordic_uart_bof.py",
        "generic_battery_spoof.py",
        "xiaomi_smartplug_bof.py",
        "fitbit_hr_spoof.py"
    ]
    for filename in exploit_files:
        url = f"{GITHUB_EXPLOITS_RAW_BASE}/{filename}"
        dest_path = os.path.join(EXPLOITS_DIR, filename)
        download_file(url, dest_path)

class BLEScanner:
    def __init__(self, args):
        self.args = args
        self.devices = {}
        self.exploit_modules = []
        self.hostname = socket.gethostname()
        self.load_exploits()

    def detection_callback(self, device, advertisement_data):
        if device.rssi < self.args.rssi:
            return
        if self.args.name and (not device.name or self.args.name.lower() not in device.name.lower()):
            return

        info = {
            "address": device.address,
            "name": device.name or "Unknown",
            "rssi": device.rssi,
            "service_uuids": advertisement_data.service_uuids or [],
            "manufacturer_data": {
                k: v.hex() for k, v in advertisement_data.manufacturer_data.items()
            } if advertisement_data.manufacturer_data else {}
        }

        self.devices[device.address] = info
        log(f"[BLE] {info['address']} | {info['name']} | {info['rssi']} dBm")

    def load_exploits(self):
        for file in glob.glob(f"{EXPLOITS_DIR}/*.py"):
            if file.endswith("__init__.py"):
                continue
            name = os.path.basename(file).replace(".py", "")
            try:
                spec = importlib.util.spec_from_file_location(name, file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self.exploit_modules.append(mod)
                log(f"[Exploit] Loaded {name}")
            except Exception as e:
                log(f"[!] Failed to load exploit {name}: {e}")

    async def run_scan(self):
        scanner = BleakScanner()
        scanner.register_detection_callback(self.detection_callback)
        await scanner.start()
        log(f"[Scan] Running for {self.args.duration}s...")
        await asyncio.sleep(self.args.duration)
        await scanner.stop()
        log(f"[Scan] Completed. {len(self.devices)} device(s) found.")

    def export_results(self):
        path = self.args.output
        if not path:
            return
        fmt = self.args.format.lower()
        with open(path, "w", newline="") as f:
            if fmt == "json":
                json.dump(list(self.devices.values()), f, indent=2)
            else:
                writer = csv.writer(f)
                writer.writerow(["Address", "Name", "RSSI", "Service UUIDs", "Manufacturer Data"])
                for dev in self.devices.values():
                    writer.writerow([
                        dev["address"], dev["name"], dev["rssi"],
                        ";".join(dev["service_uuids"]),
                        ";".join(f"{k}:{v}" for k, v in dev["manufacturer_data"].items())
                    ])
        log(f"[Export] Saved results to {path}")

    def upload_to_dashboard(self):
        try:
            requests.post(DASHBOARD_API, json={
                "agent": self.hostname,
                "timestamp": datetime.utcnow().isoformat(),
                "results": list(self.devices.values())
            }, timeout=10)
            log("[+] Uploaded results to dashboard")
        except Exception as e:
            log(f"[!] Dashboard upload failed: {e}")

    async def active_interrogate(self):
        for addr, info in self.devices.items():
            log(f"[+] Connecting to {addr}...")
            try:
                async with BleakClient(addr, timeout=15) as client:
                    if not await client.is_connected():
                        log(f"[-] Failed to connect to {addr}")
                        continue
                    services = await client.get_services()
                    for svc in services:
                        log(f" Service: {svc.uuid}")
                        for char in svc.characteristics:
                            log(f"  Char: {char.uuid} ({','.join(char.properties)})")
                            if "read" in char.properties:
                                await self.safe_read(client, char)
                            if "write" in char.properties:
                                await self.safe_write(client, char)
                    await self.run_exploits(client, info)
            except Exception as e:
                log(f"[!] Interrogation failed on {addr}: {e}")

    async def safe_read(self, client, char):
        try:
            val = await client.read_gatt_char(char.uuid)
            log(f"    Read: {val.hex()} | {val.decode(errors='ignore')}")
        except Exception as e:
            log(f"    Read error: {e}")

    async def safe_write(self, client, char):
        try:
            await client.write_gatt_char(char.uuid, b"\x00", response=True)
            log(f"    Wrote test byte to {char.uuid}")
        except Exception as e:
            log(f"    Write error: {e}")

    async def run_exploits(self, client, dev_info):
        name = dev_info["name"].lower()
        uuids = [s.lower() for s in dev_info.get("service_uuids", [])]
        for mod in self.exploit_modules:
            targets = getattr(mod, "TARGET_BRAND_NAMES", [])
            services = getattr(mod, "TARGET_SERVICE_UUIDS", [])
            if any(t.lower() in name for t in targets) or any(s.lower() in uuids for s in services):
                log(f"[Exploit] Launching {mod.__name__} on {dev_info['address']}")
                try:
                    await mod.run_exploit(client, dev_info)
                except Exception as e:
                    log(f"[!] Exploit failed: {e}")

    def sdr_spoof(self):
        log("[SDR] BLE spoofing mode activated (requires HackRF)")
        try:
            os.system("hackrf_transfer -f 2402000000 -s 8000000 -x 47 -b 1000000 -c ble_spoof.iq")
            log("[+] SDR spoofing signal sent.")
        except Exception as e:
            log(f"[!] SDR spoofing failed: {e}")

def parse_args():
    p = argparse.ArgumentParser(description="REDoT BLE Scanner & Exploiter")
    p.add_argument("-r", "--rssi", type=int, default=-80, help="Minimum RSSI")
    p.add_argument("-n", "--name", help="Filter by device name")
    p.add_argument("-d", "--duration", type=int, default=60, help="Scan duration in seconds")
    p.add_argument("-f", "--format", choices=["csv", "json"], default="csv", help="Export format")
    p.add_argument("-o", "--output", default=os.path.join(LOG_DIR, f"ble_scan_{int(time.time())}.csv"), help="Output file path")
    p.add_argument("-a", "--active", action="store_true", help="Interrogate discovered devices")
    p.add_argument("-u", "--update", action="store_true", help="Update exploits from GitHub")
    p.add_argument("-s", "--spoof", action="store_true", help="Trigger SDR BLE spoof via HackRF")
    return p.parse_args()

def main():
    args = parse_args()
    setup_logger(args.output + ".log")
    scanner = BLEScanner(args)

    if args.update:
        update_exploits()

    if args.spoof:
        scanner.sdr_spoof()
        return

    try:
        asyncio.run(scanner.run_scan())
        scanner.export_results()
        scanner.upload_to_dashboard()
        if args.active:
            asyncio.run(scanner.active_interrogate())
    except KeyboardInterrupt:
        log("[-] Interrupted by user")

if __name__ == "__main__":
    main()
