# stealth_agent.py
import os
import time

print("🕵️ Deploying stealth callback...")
time.sleep(1)
os.makedirs("loot/callbacks", exist_ok=True)
with open("loot/callbacks/beacon.txt", "w") as f:
    f.write("Callback triggered to https://webhook.site/redot at " + time.ctime())
print("✅ Callback file created in /loot/callbacks/beacon.txt")
