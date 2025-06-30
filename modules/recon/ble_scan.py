#!/usr/bin/env python3
# REDOT: ble_scan.py
# Real red team BLE scanner with CLI args, CSV/JSON export & basic active interrogation placeholder

import asyncio
import argparse
import logging
import time
import csv
import json
import os
from bleak import BleakScanner, BleakClient

LOG_DIR = "logs/ble_scan"
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

class BLEScanner:
    def __init__(self, rssi_threshold, name_filter, scan_duration, output_path, output_format):
        self.rssi_threshold = rssi_threshold
        self.name_filter = name_filter.lower() if name_filter else None
        self.scan_duration = scan_duration
        self.output_path = output_path
        self.output_format = output_format.lower() if output_format else "csv"
        self.devices = {}  # key: address, value: dict of info

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
            "manufacturer_data": {k: v.hex() for k, v in advertisement_data.manufacturer_data.items()} if advertisement_data.manufacturer_data else {}
        }
        # Log only new devices or updated RSSI stronger than previous
        if (device.address not in self.devices) or (info["rssi"] > self.devices[device.address]["rssi"]):
            self.devices[device.address] = info
            log(f"Discovered BLE Device: {info['address']} | Name: {info['name']} | RSSI: {info['rssi']} dBm")
            if info["service_uuids"]:
                log(f"    Service UUIDs: {', '.join(info['service_uuids'])}")
            if info["manufacturer_data"]:
                mdata_str = ", ".join(f"{k}: {v}" for k, v in info["manufacturer_data"].items())
                log(f"    Manufacturer Data: {mdata_str}")

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
        else:  # default csv
            with open(self.output_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Address", "Name", "RSSI", "Service UUIDs", "Manufacturer Data"])
                for dev in self.devices.values():
                    writer.writerow([
                        dev["address"],
                        dev["name"],
                        dev["rssi"],
                        ";".join(dev["service_uuids"]),
                        ";".join(f"{k}:{v}" for k,v in dev["manufacturer_data"].items())
                    ])
        log("Export complete.")

    async def active_interrogate(self):
        """
        Placeholder: actively connect and read services/characteristics from discovered devices.
        Extend this to your exploitation needs.
        """
        log("Starting active interrogation on discovered devices (placeholder)...")
        for addr, info in self.devices.items():
            try:
                async with BleakClient(addr) as client:
                    services = await client.get_services()
                    log(f"Device {addr} services:")
                    for svc in services:
                        log(f" - {svc.uuid}: {svc.description}")
                        # Extend: read characteristics, write payloads, etc.
            except Exception as e:
                log(f"Failed to interrogate {addr}: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="REDOT BLE Scanner")
    parser.add_argument("-r", "--rssi", type=int, default=-80, help="Minimum RSSI threshold (default: -80)")
    parser.add_argument("-n", "--name", type=str, default=None, help="Filter devices by name substring (case-insensitive)")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Scan duration in seconds (default: 60)")
    parser.add_argument("-o", "--output", type=str, default=f"{LOG_DIR}/ble_scan_results.csv", help="Output file path")
    parser.add_argument("-f", "--output-format", type=str, choices=["csv", "json"], default="csv", help="Output file format (csv or json)")
    parser.add_argument("-a", "--active", action="store_true", help="Perform active BLE service interrogation after scanning")
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logger(args.output + ".log")
    scanner = BLEScanner(args.rssi, args.name, args.duration, args.output, args.output_format)

    try:
        asyncio.run(scanner.run_scan())
        if args.active:
            asyncio.run(scanner.active_interrogate())
    except KeyboardInterrupt:
        log("Scan interrupted by user.")

if __name__ == "__main__":
    main()
