# modules/firmware/cve_autopwn.py
import os
import json
import requests
from datetime import datetime

# Define test firmware strings (replace with real input later)
firmware_strings = ['busybox v1.20.2', 'lighttpd/1.4.31']
known_vulns = {
    'busybox v1.20.2': {
        'cve': 'CVE-2013-1813',
        'summary': 'BusyBox wget allows arbitrary file overwrite',
        'severity': 'High',
        'exploit_links': {
            'exploitdb': 'https://www.exploit-db.com/exploits/26700',
            'packetstorm': 'https://packetstormsecurity.com/files/120420'
        }
    },
    'lighttpd/1.4.31': {
        'cve': 'CVE-2014-2323',
        'summary': 'Lighttpd mod_userdir local file disclosure',
        'severity': 'Medium',
        'exploit_links': {
            'exploitdb': 'https://www.exploit-db.com/exploits/32742',
            'packetstorm': 'https://packetstormsecurity.com/files/126068'
        }
    }
}

RESULTS_DIR = "results"
POC_DIR = os.path.join(RESULTS_DIR, "pocs")
MSF_XML_DIR = os.path.join(RESULTS_DIR, "msf_search")
KILLCHAIN_FILE = "reports/killchain.txt"
CVE_AUTOPWN_JSON = os.path.join(RESULTS_DIR, "cve_autopwn.json")

# Ensure folders exist
os.makedirs(POC_DIR, exist_ok=True)
os.makedirs(MSF_XML_DIR, exist_ok=True)
os.makedirs("reports", exist_ok=True)

matched = []

print(" CVE AutoPwn Scanner Running...")

for comp in firmware_strings:
    if comp in known_vulns:
        vuln = known_vulns[comp]
        cve_id = vuln['cve']
        print(f"[!] Found vulnerable component: {comp} => {cve_id}")
        print(f"    Suggested PoC: {vuln['exploit_links']['exploitdb']}")

        # Download PoC HTMLs
        for label, url in vuln['exploit_links'].items():
            try:
                resp = requests.get(url, timeout=10)
                poc_path = os.path.join(POC_DIR, f"{cve_id}_{label}.html")
                with open(poc_path, "w") as f:
                    f.write(resp.text)
                print(f"    [+] Saved PoC: {poc_path}")
            except Exception as e:
                print(f"    [!] Failed to download {label} PoC: {e}")

        # Write Metasploit search XML placeholder
        try:
            xml_path = os.path.join(MSF_XML_DIR, f"{cve_id}_search.xml")
            with open(xml_path, "w") as f:
                f.write(f"<metasploit><search><cve>{cve_id}</cve><result>placeholder</result></search></metasploit>")
            print(f"    [+] Metasploit XML created: {xml_path}")
        except Exception as e:
            print(f"    [!] Failed to write XML: {e}")

        # Append to killchain.txt
        try:
            with open(KILLCHAIN_FILE, "a") as f:
                f.write(f"\n[+] CVE AutoPwn Enrichment - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-> Component: {comp}\n")
                f.write(f"   - CVE: {cve_id}\n")
                f.write(f"   - Severity: {vuln['severity']}\n")
                f.write(f"   - Summary: {vuln['summary']}\n")
                for label, url in vuln['exploit_links'].items():
                    f.write(f"   - {label.upper()} PoC: {url}\n")
                f.write(f"   - Metasploit XML: {xml_path}\n")
        except Exception as e:
            print(f"    [!] Killchain update failed: {e}")

        # Track match
        matched.append({
            "component": comp,
            "cve": cve_id,
            "summary": vuln['summary'],
            "severity": vuln['severity'],
            "exploit_links": vuln['exploit_links']
        })

# Save match JSON
try:
    with open(CVE_AUTOPWN_JSON, "w") as f:
        json.dump(matched, f, indent=2)
    print(f"\n[+] Match data saved to {CVE_AUTOPWN_JSON}")
except Exception as e:
    print(f"[!] Failed to write CVE match JSON: {e}")
