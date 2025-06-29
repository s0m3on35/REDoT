#!/usr/bin/env python3
import time
import random
import argparse
import subprocess
from datetime import datetime
import sys
import os

def generate_uid():
    return ":".join(f"{random.randint(0,255):02X}" for _ in range(6))

def get_mac(interface):
    try:
        result = subprocess.run(["cat", f"/sys/class/net/{interface}/address"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception:
        return None

def set_mac(interface, mac):
    subprocess.run(["ip", "link", "set", interface, "down"])
    subprocess.run(["ip", "link", "set", interface, "address", mac])
    subprocess.run(["ip", "link", "set", interface, "up"])

def export_command(uid, target):
    if target == 'flipper':
        return f"rfid send --uid {uid}"
    elif target == 'hackrf':
        return f"hackrf_transfer -t uid_{uid.replace(':', '')}.bin -f 13.56e6"
    elif target == 'proxmark':
        return f"hf 14a sim -u {uid.replace(':', '')}"
    else:
        return None

def save_uid_binary(uid, filename):
    try:
        hex_bytes = bytes(int(b, 16) for b in uid.split(":"))
        with open(filename, 'wb') as f:
            f.write(hex_bytes)
    except Exception as e:
        print(f"[!] Failed to write UID binary: {e}")

def generate_random_pins(length=10):
    return [f"{random.randint(0, 9999):04d}" for _ in range(length)]

def flipper_feedback():
    print("\a")  # Terminal bell as simulation

# Argument parser
parser = argparse.ArgumentParser(description="Simulate RFID/UHF tag replay and PIN brute force.")
parser.add_argument('--uid', help='Specify a fixed RFID UID to clone')
parser.add_argument('--brute', action='store_true', help='Enable PIN brute-force simulation')
parser.add_argument('--random-pins', type=int, default=10, help='Number of random PINs to generate')
parser.add_argument('--correct-pin', help='Simulate access granted if this PIN is found')
parser.add_argument('--export', choices=['flipper', 'hackrf', 'proxmark'], help='Export command for device')
parser.add_argument('--delay', type=float, default=0.5, help='Delay between attempts (seconds)')
parser.add_argument('--log', default='replay_log.txt', help='Log file output')
parser.add_argument('--mac-random', action='store_true', help='Randomize MAC address temporarily')
parser.add_argument('--mac-set', help='Set custom MAC address')
parser.add_argument('--iface', default='wlan0', help='Interface for MAC operations')
parser.add_argument('--flipper-fx', action='store_true', help='Trigger Flipper-style feedback on success')
args = parser.parse_args()

original_mac = get_mac(args.iface)
new_mac = None

if args.mac_random:
    new_mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
    print(f"[+] Randomizing MAC address on {args.iface}: {new_mac}")
    set_mac(args.iface, new_mac)
elif args.mac_set:
    new_mac = args.mac_set
    print(f"[+] Setting MAC address on {args.iface} to {new_mac}")
    set_mac(args.iface, new_mac)

uid = args.uid if args.uid else generate_uid()
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f"\n[+] Access Replay Simulation")
print(f"[{timestamp}] UID cloned: {uid}")
print(" -> Sending cloned signal to controller...")
time.sleep(args.delay)
print(" -> Access response: [DENIED]")

if args.export == 'hackrf':
    fname = f"uid_{uid.replace(':','')}.bin"
    save_uid_binary(uid, fname)
    print(f"[+] UID binary saved to: {fname}")

if args.brute:
    pins = generate_random_pins(args.random_pins)
    print("\n[!] Starting randomized PIN brute-force...")
    for pin in pins:
        time.sleep(args.delay)
        print(f" -> Trying PIN {pin}...", end=' ')
        if args.correct_pin and pin == args.correct_pin:
            print("[SUCCESS]")
            if args.flipper_fx:
                flipper_feedback()
            break
        else:
            print("[FAIL]")
    else:
        print(" -> Max attempts reached. Lockout triggered.")

if args.export:
    print(f"\n[+] Suggested command for {args.export}:")
    print(f"    {export_command(uid, args.export)}")

if new_mac and original_mac:
    print(f"\n[+] Restoring MAC address to: {original_mac}")
    set_mac(args.iface, original_mac)

with open(args.log, 'a') as log:
    log.write(f"{timestamp} - UID: {uid}\n")
    if args.brute:
        log.write(f"    Random PINs tried: {args.random_pins}\n")
        if args.correct_pin:
            log.write(f"    Correct PIN simulated: {args.correct_pin}\n")
    if args.export:
        log.write(f"    Export target: {args.export}\n")
    if new_mac:
        log.write(f"    MAC spoofed to {new_mac}, restored to {original_mac}\n")

print(f"\n[+] Simulation complete. Log saved to {args.log}")
