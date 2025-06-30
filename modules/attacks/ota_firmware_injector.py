
import os, time, json

AGENT_ID = "ota_injector"
ALERT_FILE = "webgui/alerts.json"

def log(msg):
    print(f"[OTA] {msg}")

def inject_firmware():
    os.makedirs("reports", exist_ok=True)
    log("Interception simulated... Injecting payload")
    with open("reports/ota_firmware.bin", "wb") as f:
        f.write(b"INJECTED_FIRMWARE_PAYLOAD")
    log("Payload written to reports/ota_firmware.bin")

def push_alert():
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": AGENT_ID,
            "alert": "OTA firmware interceptor triggered",
            "type": "firmware",
            "timestamp": time.time()
        }) + "\n")

def main():
    inject_firmware()
    push_alert()

if __name__ == "__main__":
    main()
