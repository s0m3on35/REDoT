#!/usr/bin/env python3

import os, argparse, subprocess, json
from datetime import datetime

LOG_FILE = "results/edid_injector_logs.json"
MITRE_TTP = "T1200"

def log_injection(data):
    os.makedirs("results", exist_ok=True)
    existing = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            existing = json.load(f)
    existing.append(data)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

def inject_edid(edid_file, output):
    try:
        subprocess.run(["xrandr", "--output", output, "--set", "EDID", edid_file], check=True)
        return True
    except Exception as e:
        print(f"[!] EDID injection failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Inject fake EDID via xrandr")
    parser.add_argument("--edid", required=True, help="Path to .bin EDID file")
    parser.add_argument("--output", required=True, help="Display output (e.g., HDMI-1)")
    args = parser.parse_args()

    result = inject_edid(args.edid, args.output)
    log_injection({
        "timestamp": datetime.utcnow().isoformat(),
        "edid_file": args.edid,
        "output": args.output,
        "success": result,
        "ttp": MITRE_TTP
    })

if __name__ == "__main__":
    main()
