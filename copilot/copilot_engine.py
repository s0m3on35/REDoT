#!/usr/bin/env python3
"""
copilot_engine.py – REDOT GPT Copilot Logic Engine
Simulates GPT-style recon analysis and module recommendations
"""

import os
import random
import time

LOG_DIR = "logs"
RECOMMENDATIONS = {
    "wifi_scan": [
        "Consider launching 'wifi_attack.py' to impersonate SSIDs found.",
        "Run 'implant_dropper.py' after Evil Twin to persist in victim devices."
    ],
    "ble_crasher": [
        "Deploy 'stealth_agent.py' to BLE-connected targets after crash.",
        "Replay BLE signals using 'rf_signal_cloner.py'."
    ],
    "rf_signal_cloner": [
        "Export RF replay to Flipper via '.sub' file.",
        "Schedule replay via 'watering_loop.sh' on known RF devices."
    ],
    "cve_autopwn": [
        "Run 'firmware_poisoner.py' to inject payloads into matching binaries.",
        "Generate kill chain with 'killchain_builder.py' for documentation."
    ],
    "uart_extractor": [
        "Analyze output for hardcoded creds or debug UART commands.",
        "Use 'dashboard_override.py' to push automation bypasses."
    ],
    "wifi_attack": [
        "Monitor for victims with dashboard live mode.",
        "Auto-chain to 'implant_dropper.py' for callbacks."
    ],
    "implant_dropper": [
        "Confirm callback beacon in dashboard.",
        "Push remote command using 'cmd_server.py'."
    ]
}

def detect_completed_modules():
    completed = []
    if not os.path.isdir(LOG_DIR):
        return completed
    for file in os.listdir(LOG_DIR):
        if file.endswith(".log"):
            mod = file.replace(".log", "")
            completed.append(mod)
    return completed

def suggest_next_steps(completed):
    print("\n[+] GPT Copilot Suggestions Based on Current Recon:\n")
    seen = set()
    for mod in completed:
        suggestions = RECOMMENDATIONS.get(mod, [])
        for s in suggestions:
            if s not in seen:
                print(f" • {s}")
                seen.add(s)
    if not seen:
        print(" • No actionable suggestions found. Run recon modules first.")

def summarize_environment(modules):
    print("\n[+] Summary of Completed Modules:\n")
    for mod in modules:
        print(f" - {mod} ok ")

def main():
    print("=== REDOT Copilot Engine ===")
    print(" [AI GPT Recon Advisor]\n")

    completed = detect_completed_modules()
    summarize_environment(completed)
    suggest_next_steps(completed)

if __name__ == "__main__":
    main()
