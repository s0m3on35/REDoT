#!/usr/bin/env python3
import os
import json
import glob
import asyncio
import websockets
from datetime import datetime

# Required paths
report_dir = "reports"
results_dir = "results"
trigger_dir = "dashboard/triggers"
trigger_file = os.path.join(trigger_dir, "trigger_report.json")
report_path = os.path.join(report_dir, "redot_report.md")

# Ensure folders exist
os.makedirs(report_dir, exist_ok=True)
os.makedirs(results_dir, exist_ok=True)
os.makedirs(trigger_dir, exist_ok=True)

# Default sets
assets = set()
modules_used = set()
cves = set()

def load_results():
    for path in glob.glob(f"{results_dir}/*.json"):
        modules_used.add(os.path.basename(path).replace(".json", ""))
        try:
            with open(path) as f:
                data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        ip = entry.get("IP") or entry.get("ip")
                        name = entry.get("Host") or entry.get("device") or ""
                        if ip or name:
                            asset_str = f"{ip or name} - {name or ip or 'Unknown'}"
                            assets.add(asset_str)
                        cve = entry.get("CVE") or entry.get("cve")
                        if cve:
                            if isinstance(cve, list):
                                for item in cve:
                                    cves.add(item)
                            else:
                                cves.add(str(cve))
        except Exception as e:
            print(f"[!] Failed to parse {path}: {e}")

def get_agent_id():
    if os.path.exists(trigger_file):
        try:
            with open(trigger_file) as f:
                data = json.load(f)
                return data.get("agent_id", "unknown-agent")
        except Exception:
            return "unknown-agent"
    else:
        # Auto-create default trigger file
        with open(trigger_file, "w") as f:
            json.dump({"agent_id": "unknown-agent"}, f, indent=2)
        return "unknown-agent"

def write_report(agent_id):
    with open(report_path, "w") as f:
        f.write(f"# REDoT Attack Summary Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Agent ID: {agent_id}\n\n")

        f.write("## Target Assets\n")
        for asset in sorted(assets):
            f.write(f"- {asset}\n")

        f.write("\n## Modules Deployed\n")
        for mod in sorted(modules_used):
            f.write(f"- {mod}.py\n")

        f.write("\n## CVEs Matched\n")
        for cve in sorted(cves):
            f.write(f"- {cve}\n")

        f.write("\n## Suggested Next Steps\n")
        f.write("- Run `dashboard_override.py` to manipulate dashboards\n")
        f.write("- Trigger `loop_bomb.py` on MQTT or HTTP targets\n")
        f.write("- Launch `dns_c2.py` to monitor covert channels\n")

    print(f"[+] Markdown report written to: {report_path}")

async def push_to_dashboard(agent_id):
    try:
        async with websockets.connect("ws://localhost:8765") as ws:
            await ws.send(json.dumps({
                "type": "report_summary",
                "agent": agent_id,
                "timestamp": datetime.now().isoformat(),
                "assets": list(assets),
                "modules": list(modules_used),
                "cves": list(cves),
                "file": report_path
            }))
            print("[+] Report pushed to dashboard WebSocket")
    except Exception as e:
        print(f"[!] WebSocket push failed: {e}")

# Execute
if __name__ == "__main__":
    print("== REDoT Report Builder ==")
    load_results()
    agent_id = get_agent_id()
    write_report(agent_id)
    asyncio.run(push_to_dashboard(agent_id))
