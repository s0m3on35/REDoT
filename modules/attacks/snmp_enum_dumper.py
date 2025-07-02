# modules/attacks/snmp_enum_dumper.py

import subprocess
import argparse
import json
from datetime import datetime
import os

LOG_PATH = "results/snmp_enum_results.json"
MITRE_TTP = "T1046"

def log_result(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def run_snmpwalk(target_ip, community, oid):
    try:
        result = subprocess.check_output(["snmpwalk", "-v2c", "-c", community, target_ip, oid], stderr=subprocess.DEVNULL)
        return result.decode()
    except Exception:
        return ""

def dump_all(target_ip, community):
    results = {
        "system": run_snmpwalk(target_ip, community, "1.3.6.1.2.1.1"),
        "interfaces": run_snmpwalk(target_ip, community, "1.3.6.1.2.1.2"),
        "routing": run_snmpwalk(target_ip, community, "1.3.6.1.2.1.4.21")
    }
    log_result({
        "timestamp": datetime.utcnow().isoformat(),
        "target": target_ip,
        "community": community,
        "data": results,
        "ttp": MITRE_TTP
    })
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SNMP Enumeration Dumper (v2c)")
    parser.add_argument("--ip", required=True, help="Target device IP")
    parser.add_argument("--community", default="public", help="SNMP community string")
    args = parser.parse_args()

    results = dump_all(args.ip, args.community)
    for section, content in results.items():
        print(f"\n[{section.upper()}]\n{content}")
