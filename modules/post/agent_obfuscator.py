#!/usr/bin/env python3
# modules/post/agent_obfuscator.py

import os
import hashlib
import random
import json
from datetime import datetime

AGENT_LOG_DIR = "logs/agents/"
AGENT_JSON_PATH = "webgui/agents.json"
OBFUSCATION_LOG = "logs/obfuscation_history.json"

def hash_filename(original):
    return hashlib.sha256(original.encode()).hexdigest()[:12]

def obfuscate_agent_log_files():
    if not os.path.exists(AGENT_LOG_DIR):
        os.makedirs(AGENT_LOG_DIR, exist_ok=True)
        return []

    renamed = []
    for fname in os.listdir(AGENT_LOG_DIR):
        original_path = os.path.join(AGENT_LOG_DIR, fname)
        if not os.path.isfile(original_path):
            continue
        new_name = hash_filename(fname) + ".log"
        new_path = os.path.join(AGENT_LOG_DIR, new_name)
        os.rename(original_path, new_path)
        renamed.append((fname, new_name))
    return renamed

def obfuscate_agents_json():
    if not os.path.exists(AGENT_JSON_PATH):
        return []

    with open(AGENT_JSON_PATH, "r") as f:
        data = json.load(f)

    for agent in data:
        agent['name'] = "agent-" + hashlib.md5(agent['name'].encode()).hexdigest()[:6]
        agent['ip'] = "10." + ".".join(str(random.randint(0, 255)) for _ in range(3))

    with open(AGENT_JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)

    return data

def save_obfuscation_log(renamed_files, obfuscated_agents):
    history = {
        "timestamp": datetime.utcnow().isoformat(),
        "renamed_files": renamed_files,
        "agents": obfuscated_agents
    }

    if not os.path.exists(OBFUSCATION_LOG):
        full_log = [history]
    else:
        with open(OBFUSCATION_LOG, "r") as f:
            try:
                full_log = json.load(f)
            except Exception:
                full_log = []

        full_log.append(history)

    with open(OBFUSCATION_LOG, "w") as f:
        json.dump(full_log, f, indent=2)

def main():
    print("=== REDOT Agent Obfuscator ===")
    renamed = obfuscate_agent_log_files()
    print(f"[+] Obfuscated {len(renamed)} agent log files.")

    agents = obfuscate_agents_json()
    print(f"[+] Obfuscated {len(agents)} agents in agents.json.")

    save_obfuscation_log(renamed, agents)
    print(f"[✓] Obfuscation record saved to {OBFUSCATION_LOG}")

if __name__ == "__main__":
    main()
