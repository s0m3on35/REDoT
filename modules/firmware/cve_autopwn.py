#!/usr/bin/env python3
import os
import json
import requests
import subprocess
from datetime import datetime

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
POST_MODULES = ["modules/payloads/dns_c2.py", "modules/payloads/implant_dropper.py"]

def check_write(path):
    try:
        os.makedirs(path, exist_ok=True)
        testfile = os.path.join(path, ".__testwrite__")
        with open(testfile, "w") as f:
            f.write("test")
        os.remove(testfile)
        return True
    except:
        return False

def launch_post_modules():
    for module in POST_MODULES:
        if os.path.exists(module):
            try:
                subprocess.Popen(["python3", module], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[+] Post-ex module launched: {module}")
            except:
                pass

def launch_metasploit(cve_id):
    msf_cmd = f"search {cve_id}"
    try:
        print(f"[>] Launching Metasploit for CVE: {cve_id}")
        subprocess.call(["msfconsole", "-q", "-x", f"{msf_cmd}; exit"])
    except:
        print(f"[!] Metasploit launch failed for {cve_id}")

if not check_write(RESULTS_DIR) or not check_write("reports"):
    print("[!] Check write permissions on results/ and reports/")
    exit(1)

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

        for label, url in vuln['exploit_links'].items():
            try:
                resp = requests.get(url, timeout=10)
                poc_path = os.path.join(POC_DIR, f"{cve_id}_{label}.html")
                with open(poc_path, "w") as f:
                    f.write(resp.text)
                print(f"    [+] Saved PoC: {poc_path}")
            except:
                print(f"    [!] Failed to download {label} PoC")

        try:
            xml_path = os.path.join(MSF_XML_DIR, f"{cve_id}_search.xml")
            with open(xml_path, "w") as f:
                f.write(f"<metasploit><search><cve>{cve_id}</cve><result>placeholder</result></search></metasploit>")
            print(f"    [+] Metasploit XML created: {xml_path}")
        except:
            print(f"    [!] Failed to write XML")

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
        except:
            print(f"    [!] Killchain update failed")

        matched.append({
            "component": comp,
            "cve": cve_id,
            "summary": vuln['summary'],
            "severity": vuln['severity'],
            "exploit_links": vuln['exploit_links']
        })

        choice = input(f"    [>] Launch Metasploit for {cve_id}? (y/n): ").strip().lower()
        if choice == 'y':
            launch_metasploit(cve_id)

try:
    with open(CVE_AUTOPWN_JSON, "w") as f:
        json.dump(matched, f, indent=2)
    print(f"\n[+] Match data saved to {CVE_AUTOPWN_JSON}")
except:
    print(f"[!] Failed to write CVE match JSON")

print("\n[>] Launching post-ex modules...")
launch_post_modules()
