# report_builder.py - Generate Attack Summary Report
import os
from datetime import datetime

report_path = "reports/redot_report.md"
os.makedirs("reports", exist_ok=True)

# Simulated log-based asset summary
assets = ["192.168.1.100 - RTSP Camera", "192.168.1.50 - Dashboard", "gardenbot-01.local - MQTT Bot"]
cves = ["CVE-2014-2323", "CVE-2013-1813"]
modules_used = ["wifi_scan", "rf_signal_cloner", "cve_autopwn", "firmware_poisoner", "dns_c2"]

with open(report_path, "w") as f:
    f.write(f"# RedOT Attack Report\n")
    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    f.write("## 🎯 Target Assets\n")
    for asset in assets:
        f.write(f"- {asset}\n")

    f.write("\n## 🔍 CVEs Matched\n")
    for cve in cves:
        f.write(f"- {cve}\n")

    f.write("\n## 💣 Modules Deployed\n")
    for mod in modules_used:
        f.write(f"- {mod}.py\n")

    f.write("\n## ✅ Suggested Next Steps\n")
    f.write("- Run 'dashboard_override.py' to trigger rogue automations\n")
    f.write("- Deploy 'loop_bomb.py' on identified MQTT bot\n")
    f.write("- Capture DNS exfil using 'dns_c2.py' beacon listener\n")

print(f"Report generated: {report_path}")
