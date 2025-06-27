# killchain_builder.py
from datetime import datetime

steps = [
    "1. Reconnaissance",
    "2. Weaponization",
    "3. Delivery",
    "4. Exploitation",
    "5. Installation",
    "6. Command & Control",
    "7. Actions on Objectives"
]

with open("reports/killchain.txt", "w") as f:
    f.write(f"📆 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    for s in steps:
        f.write(f"{s}\n")
        f.write("- Tool: TBD\n")
        f.write("- Notes: TBD\n\n")

print("✅ Kill Chain initialized: reports/killchain.txt")
