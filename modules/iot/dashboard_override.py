# Home Automation Dashboard Override
print("📊 Dashboard Override Module")

dashboards = ['http://192.168.1.50:8123', 'http://192.168.1.51:8080']
for url in dashboards:
    print(f"[+] Probing {url}...")
    print("    -> Attempting default login (admin:admin)... [FAIL]")
    print("    -> Attempting CVE exploit for remote command injection... [SUCCESS]")
    print(f"    -> Injected rogue automation: 'Turn off lights every 5 sec' at {url}")
