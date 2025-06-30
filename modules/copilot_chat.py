import readline
import json
import os
from datetime import datetime

LOG_FILE = "logs/copilot_chat.log"
SUGGESTIONS = {
    "firmware": [
        "Run 'firmware_poisoner.py' to embed payloads",
        "Use 'cve_autopwn.py' to find exploitable strings"
    ],
    "wifi": [
        "Use 'wifi_attack.py' to deploy Evil Twin",
        "Enable auto-chain to 'implant_dropper.py' from the captive portal"
    ],
    "rf": [
        "Replay signals with 'rf_signal_cloner.py'",
        "Use 'loop_bomb.py' to simulate watering chaos"
    ],
    "ble": [
        "Jam with 'ble_crasher.py'",
        "Scan for characteristics with BLE toolkit integration"
    ],
    "voice": [
        "Trigger ultrasonic payload via 'voice_injection.py'",
        "Switch mode in dashboard to 'ultrasonic'"
    ],
    "dashboard": [
        "Inject overrides using 'dashboard_override.py'",
        "Monitor camera feed with 'cam_spoof.py'"
    ],
    "implant": [
        "Check callback in 'agents.json'",
        "Trigger persistence via 'stealth_agent.py'"
    ]
}

def log_entry(entry):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {entry}\n")

print(" RedOT Copilot Chat – Ask me anything (type 'exit' to quit):")

while True:
    user_input = input("> ").strip().lower()
    log_entry(user_input)
    if user_input == "exit":
        break

    suggestions_found = False
    for keyword, responses in SUGGESTIONS.items():
        if keyword in user_input:
            for suggestion in responses:
                print(f"- {suggestion}")
            suggestions_found = True
            break

    if not suggestions_found:
        print("- No direct match found. Consider running 'wifi_scan.py' or checking the dashboard.")
