# CVE Autopwn Module
import os
print(" CVE AutoPwn Scanner Running...")
# Simulated parsing and matching
firmware_strings = ['busybox v1.20.2', 'lighttpd/1.4.31']
known_vulns = {
    'busybox v1.20.2': 'CVE-2013-1813',
    'lighttpd/1.4.31': 'CVE-2014-2323'
}
for comp in firmware_strings:
    if comp in known_vulns:
        print(f"[!] Found vulnerable component: {comp} => {known_vulns[comp]}")
        print(f"    Suggested PoC: https://www.exploit-db.com/search?q={known_vulns[comp]}")
