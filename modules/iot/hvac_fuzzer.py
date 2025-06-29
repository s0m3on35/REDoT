#!/usr/bin/env python3
# modules/iot/hvac_fuzzer.py

import socket
import argparse
import random
import time
import os
from datetime import datetime

MODBUS_PORT = 502
BACNET_PORT = 47808

def get_recon_targets():
    recon_file = 'recon/hvac_targets.txt'
    if os.path.exists(recon_file):
        with open(recon_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def generate_modbus_payload():
    return bytes([random.randint(0, 255) for _ in range(12)])

def generate_bacnet_payload():
    return bytes([0x81, 0x0a, 0x00, 0x10] + [random.randint(0, 255) for _ in range(8)])

def send_modbus_fuzz(target_ip, stealth):
    print(f"[+] Modbus -> {target_ip}:{MODBUS_PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((target_ip, MODBUS_PORT))
        payload = generate_modbus_payload()
        sock.send(payload)
        if stealth:
            print("    -> Sent simulated Modbus fuzz packet.")
        else:
            try:
                resp = sock.recv(64)
                print(f"    -> Real response: {resp.hex()}")
            except:
                print("    -> No response or timeout.")
        sock.close()
    except Exception as e:
        print(f"    -> Connection error: {e}")

def send_bacnet_fuzz(target_ip, stealth):
    print(f"[+] BACnet -> {target_ip}:{BACNET_PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    try:
        payload = generate_bacnet_payload()
        sock.sendto(payload, (target_ip, BACNET_PORT))
        if stealth:
            print("    -> Sent simulated BACnet fuzz packet.")
        else:
            try:
                resp, _ = sock.recvfrom(128)
                print(f"    -> Real response: {resp.hex()}")
            except:
                print("    -> No response or timeout.")
        sock.close()
    except Exception as e:
        print(f"    -> Connection error: {e}")

def export_flipper_signal(target_ip):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'exports/hvac_override_{target_ip}_{ts}.sub'
    os.makedirs('exports', exist_ok=True)
    with open(filename, 'w') as f:
        f.write("Filetype: Flipper SubGhz RAW File\n")
        f.write("Frequency: 433920000\n")
        f.write("Protocol: RAW\n")
        f.write("RAW_Data: 1000 -1000 1000 -1000 1000 -1000\n")
    print(f"    -> Exported simulated .sub RF file: {filename}")

def main():
    parser = argparse.ArgumentParser(description="HVAC Modbus/BACnet Fuzzer")
    parser.add_argument('--stealth', action='store_true', help='Run in stealth/simulated mode')
    parser.add_argument('--target', help='Specify a manual IP')
    parser.add_argument('--scan-modbus', action='store_true', help='Enable Modbus fuzzing')
    parser.add_argument('--scan-bacnet', action='store_true', help='Enable BACnet fuzzing')
    parser.add_argument('--export-sub', action='store_true', help='Export fake RF override signal')
    args = parser.parse_args()

    targets = get_recon_targets()
    if not targets and not args.target:
        print("[!] No targets found. Provide --target or populate recon/hvac_targets.txt")
        return

    if args.target:
        targets.append(args.target)

    for target in targets:
        print(f"\n=== Target: {target} ===")
        if args.scan_modbus:
            send_modbus_fuzz(target, args.stealth)
        if args.scan_bacnet:
            send_bacnet_fuzz(target, args.stealth)
        if args.export_sub:
            export_flipper_signal(target)

if __name__ == "__main__":
    main()
