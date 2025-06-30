#!/usr/bin/env python3
import json
import os
import time
import asyncio
import websockets
from datetime import datetime

killchain_steps = [
    ("1. Reconnaissance", ["wifi_attack.json", "ble_crasher.json"]),
    ("2. Weaponization", ["firmware_poisoner.log"]),
    ("3. Delivery", ["dns_c2.log"]),
    ("4. Exploitation", ["implant_dropper.log"]),
    ("5. Installation", ["stealth_agent.log"]),
    ("6. Command & Control", ["dns_c2.log"]),
    ("7. Actions on Objectives", ["post_exfiltrator.log"])
]

report_dir = "reports"
os.makedirs(report_dir, exist_ok=True)
json_out = os.path.join(report_dir, "killchain.json")
txt_out = os.path.join(report_dir, "killchain.txt")
dashboard_trigger_file = "dashboard/triggers/trigger_killchain.json"

def try_autofill(logfiles):
    for f in logfiles:
        path = os.path.join("results", f)
        if os.path.isfile(path):
            try:
                with open(path, "r") as fp:
                    content = fp.read()
                    return f"Auto from {f}: {content.strip().splitlines()[0][:100]}"
            except:
                continue
    return ""

def load_trigger():
    if os.path.exists(dashboard_trigger_file):
        with open(dashboard_trigger_file) as f:
            try:
                data = json.load(f)
                return data.get("agent_id", "N/A")
            except:
                return "N/A"
    return "N/A"

killchain_data = {
    "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    "agent_id": load_trigger(),
    "phases": []
}

print("== REDoT Kill Chain Builder ==")

for step, logs in killchain_steps:
    print(f"\n{step}")
    default_tool = try_autofill(logs)
    if default_tool:
        print(f"  [Autofill] Suggested: {default_tool}")
    tool = input("  Tool used (enter to accept autofill): ").strip() or default_tool
    notes = input("  Notes: ").strip()
    killchain_data["phases"].append({
        "step": step,
        "tool": tool,
        "notes": notes
    })

with open(json_out, "w") as f:
    json.dump(killchain_data, f, indent=2)

with open(txt_out, "w") as f:
    f.write(f"Generated: {killchain_data['generated_at']} | Agent: {killchain_data['agent_id']}\n\n")
    for phase in killchain_data["phases"]:
        f.write(f"{phase['step']}\n")
        f.write(f"- Tool: {phase['tool']}\n")
        f.write(f"- Notes: {phase['notes']}\n\n")

print(f"\nKill Chain saved to {txt_out}")
print(f"JSON saved to {json_out}")

async def push_to_dashboard(data):
    try:
        async with websockets.connect("ws://localhost:8765") as ws:
            await ws.send(json.dumps({
                "type": "killchain_report",
                "agent": killchain_data["agent_id"],
                "timestamp": killchain_data["generated_at"],
                "data": data
            }))
            print("Report pushed to dashboard.")
    except Exception as e:
        print("WebSocket push failed:", e)

asyncio.run(push_to_dashboard(killchain_data))
