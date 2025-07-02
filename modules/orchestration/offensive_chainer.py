# modules/orchestration/offensive_chainer.py

import os
import json
import argparse
import subprocess
from datetime import datetime

CHAIN_LOG = "results/attack_chains.json"

def load_chain_config(config_path):
    with open(config_path, "r") as f:
        return json.load(f)

def log_chain_execution(chain):
    os.makedirs("results", exist_ok=True)
    log = []
    if os.path.exists(CHAIN_LOG):
        with open(CHAIN_LOG, "r") as f:
            log = json.load(f)
    log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "executed_chain": chain
    })
    with open(CHAIN_LOG, "w") as f:
        json.dump(log, f, indent=2)

def execute_chain(chain):
    for step in chain:
        module = step.get("module")
        args = step.get("args", "")
        full_cmd = f"python3 {module} {args}"
        print(f"[+] Executing: {full_cmd}")
        subprocess.call(full_cmd, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dynamic REDoT Offensive Chain Executor")
    parser.add_argument("--config", required=True, help="Path to attack chain config JSON")
    args = parser.parse_args()

    chain = load_chain_config(args.config)
    execute_chain(chain)
    log_chain_execution(chain)
