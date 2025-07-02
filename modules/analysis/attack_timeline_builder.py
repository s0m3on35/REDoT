# modules/analysis/attack_timeline_builder.py

import os
import json
from datetime import datetime

LOG_DIR = "results"
OUT_PATH = "results/attack_timeline.json"

def collect_logs():
    timeline = []
    for file in os.listdir(LOG_DIR):
        if file.endswith(".json"):
            try:
                with open(os.path.join(LOG_DIR, file), "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for entry in data:
                            entry["_source_file"] = file
                            timeline.append(entry)
            except Exception:
                continue
    return timeline

def build_timeline():
    timeline = collect_logs()
    timeline.sort(key=lambda x: x.get("timestamp", ""))
    with open(OUT_PATH, "w") as f:
        json.dump(timeline, f, indent=2)
    print(f"[✓] Attack timeline written to {OUT_PATH}")

if __name__ == "__main__":
    build_timeline()
