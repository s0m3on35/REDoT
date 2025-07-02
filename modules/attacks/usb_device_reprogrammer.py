#!/usr/bin/env python3

import os, subprocess, argparse, json
from datetime import datetime

LOG_FILE = "results/usb_reprogram_log.json"
MITRE_TTP = "T1200"

def log_action(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def reprogram_usb(firmware_path, vendor_id, product_id, method="dfu"):
    try:
        if method == "dfu":
            cmd = ["dfu-util", "-d", f"{vendor_id}:{product_id}", "-D", firmware_path]
        elif method == "fxload":
            cmd = ["fxload", "-t", "fx2", "-D", f"{vendor_id}:{product_id}", "-I", firmware_path]
        else:
            return False
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        return False

def main():
    parser = argparse.ArgumentParser(description="Reprogram USB device firmware")
    parser.add_argument("--fw", required=True, help="Firmware binary path")
    parser.add_argument("--vid", required=True, help="Vendor ID")
    parser.add_argument("--pid", required=True, help="Product ID")
    parser.add_argument("--method", choices=["dfu", "fxload"], default="dfu")
    args = parser.parse_args()

    success = reprogram_usb(args.fw, args.vid, args.pid, args.method)
    log_action({
        "timestamp": datetime.utcnow().isoformat(),
        "vendor_id": args.vid,
        "product_id": args.pid,
        "firmware": args.fw,
        "method": args.method,
        "success": success,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
