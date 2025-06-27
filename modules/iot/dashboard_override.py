# Home Automation Dashboard Override
print(" Dashboard Override Module")

dashboards = ['http://192.x.1.x:8123', 'http://192.x.1.x:8080']
for url in dashboards:
    print(f"[+] Probing {url}...")
    print("    -> Attempting default login (admin:admin)... [FAIL]")
    print("    -> Attempting CVE exploit for remote command injection... [SUCCESS]")
    print(f"    -> Injected rogue automation: 'Turn off lights every 5 sec' at {url}")
