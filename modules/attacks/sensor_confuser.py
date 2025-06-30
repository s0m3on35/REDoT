
import os, json, time

AGENT_ID = "sensor_confuser"
ALERT_FILE = "webgui/alerts.json"

def log(msg):
    print(f"[SENSOR] {msg}")

def push_alert():
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": AGENT_ID,
            "alert": "Sensor spoof injection running",
            "type": "sensor",
            "timestamp": time.time()
        }) + "\n")

def main():
    log("Injecting spoofed temperature = 200C")
    push_alert()
    time.sleep(2)
    log("Injection complete.")

if __name__ == "__main__":
    main()
