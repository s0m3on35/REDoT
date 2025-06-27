# intel_enricher.py
import json
import requests

# Placeholder keys
SHODAN_API_KEY = "YOUR_SHODAN_KEY"
CENSYS_API_ID = "YOUR_CENSYS_ID"
CENSYS_SECRET = "YOUR_CENSYS_SECRET"

target_ip = input("Target IP: ")

print("🔍 Searching Shodan...")
shodan_url = f"https://api.shodan.io/shodan/host/{target_ip}?key={SHODAN_API_KEY}"
try:
    shodan_data = requests.get(shodan_url).json()
    print("Shodan OS:", shodan_data.get("os", "N/A"))
    print("Ports:", shodan_data.get("ports", []))
except Exception as e:
    print("❌ Shodan error:", e)

print("\n🔍 Searching Censys...")
censys_url = "https://search.censys.io/api/v2/hosts/" + target_ip
try:
    resp = requests.get(censys_url, auth=(CENSYS_API_ID, CENSYS_SECRET))
    if resp.status_code == 200:
        print("Censys result:", resp.json().get("result", {}).get("services", []))
    else:
        print("Censys error:", resp.status_code)
except Exception as e:
    print("❌ Censys error:", e)
