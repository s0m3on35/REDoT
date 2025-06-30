# modules/intel_enricher.py
import json
import requests
import os
import time
import threading
import websocket

# Load keys from config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config/intel_keys.json")
try:
    with open(CONFIG_PATH, "r") as f:
        keys = json.load(f)
        SHODAN_API_KEY = keys["shodan"]
        CENSYS_API_ID = keys["censys_id"]
        CENSYS_SECRET = keys["censys_secret"]
except Exception as e:
    print(f"Config load error: {e}")
    exit(1)

target_ip = input("Target IP: ").strip()
if not target_ip:
    print("No IP provided. Exiting.")
    exit()

results = {"ip": target_ip, "timestamp": time.time()}

def query_shodan():
    print("Querying Shodan...")
    try:
        url = f"https://api.shodan.io/shodan/host/{target_ip}?key={SHODAN_API_KEY}"
        data = requests.get(url).json()
        results["shodan_os"] = data.get("os", "N/A")
        results["shodan_ports"] = data.get("ports", [])
    except Exception as e:
        results["shodan_error"] = str(e)

def query_censys():
    print("Querying Censys...")
    try:
        url = f"https://search.censys.io/api/v2/hosts/{target_ip}"
        r = requests.get(url, auth=(CENSYS_API_ID, CENSYS_SECRET))
        if r.status_code == 200:
            results["censys_services"] = r.json().get("result", {}).get("services", [])
        else:
            results["censys_error"] = f"HTTP {r.status_code}"
    except Exception as e:
        results["censys_error"] = str(e)

# Run both queries in parallel
threads = [threading.Thread(target=query_shodan), threading.Thread(target=query_censys)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Log results locally
log_dir = os.path.join(os.path.dirname(__file__), "../../logs")
os.makedirs(log_dir, exist_ok=True)
with open(os.path.join(log_dir, f"intel_enrich_{target_ip.replace('.', '_')}.json"), "w") as f:
    json.dump(results, f, indent=2)

print("\nEnrichment complete. Summary:")
for k, v in results.items():
    print(f"{k}: {v}")

# Optional WebSocket broadcast to dashboard
def send_to_dashboard(data):
    try:
        ws = websocket.create_connection("ws://localhost:8765")
        ws.send(json.dumps({"type": "intel_enrich", "data": data}))
        ws.close()
    except Exception as e:
        print(f"WebSocket error: {e}")

send_to_dashboard(results)
