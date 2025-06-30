import argparse
import os
import json
import time
import numpy as np
from datetime import datetime
from scipy.stats import entropy

AGENT_ID = "entropy_analyzer"
ALERT_FILE = "webgui/alerts.json"
KILLCHAIN_FILE = "reports/killchain.json"

def log(msg):
    print(f"[ENTROPY] {msg}")

def push_alert(score, path):
    alert = {
        "agent": AGENT_ID,
        "alert": f"Entropy score: {score:.2f} for {os.path.basename(path)}",
        "type": "signal_analysis",
        "timestamp": time.time()
    }
    os.makedirs("webgui", exist_ok=True)
    with open(ALERT_FILE, "a") as f:
        f.write(json.dumps(alert) + "\n")

def log_killchain(path, score):
    os.makedirs("reports", exist_ok=True)
    entry = {
        "agent": AGENT_ID,
        "technique": "RF Entropy Analysis",
        "file": path,
        "entropy_score": score,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if os.path.exists(KILLCHAIN_FILE):
        with open(KILLCHAIN_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(KILLCHAIN_FILE, "w") as f:
        json.dump(data, f, indent=2)

def analyze_entropy(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    values, counts = np.unique(list(data), return_counts=True)
    dist = counts / counts.sum()
    score = entropy(dist, base=2)
    log(f"Entropy of {filepath}: {score:.2f}")
    push_alert(score, filepath)
    log_killchain(filepath, score)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to RF binary input (.sub/.bin)")
    args = parser.parse_args()
    analyze_entropy(args.input)
