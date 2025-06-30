
import time, json, os

AGENT_ID = "relay_attack"
ALERT_FILE = "webgui/alerts.json"

def log(msg):
    print(f"[RELAY] {msg}")

def push_alert():
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps({
            "agent": AGENT_ID,
            "alert": "Proximity relay spoof initiated",
            "type": "relay",
            "timestamp": time.time()
        }) + "\n")

def main():
    log("Simulating BLE/UWB relay spoof...")
    push_alert()
    time.sleep(3)
    log("Replay of access signal triggered.")

if __name__ == "__main__":
    main()
