#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

print("🔧 Starting JTAG Auto Interface Discovery...")

# Ensure output folder
os.makedirs("logs", exist_ok=True)
dump_path = f"logs/jtag_flash_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"

# Check for OpenOCD availability
def check_openocd():
    try:
        subprocess.run(["openocd", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

if not check_openocd():
    print("[!] OpenOCD not found. Please install it to proceed.")
    exit(1)

# Create minimal OpenOCD config file
config_path = "logs/openocd_auto.cfg"
with open(config_path, "w") as cfg:
    cfg.write("""
interface ft2232
ft2232_vid_pid 0x0403 0x6010
ft2232_layout jtagkey
transport select jtag
reset_config trst_and_srst
adapter_khz 1000

# Replace with actual target chip config
source [find target/stm32f1x.cfg]
""")

print(f"[+] OpenOCD config generated at: {config_path}")
print("[*] Attempting to connect and dump flash...")

# Start OpenOCD with commands to dump flash
try:
    result = subprocess.run([
        "openocd", "-f", config_path,
        "-c", f"init; reset halt; dump_image {dump_path} 0x08000000 0x10000; shutdown"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    if result.returncode == 0:
        print(f"[+] Flash memory dumped to {dump_path}")
    else:
        print("[!] Dump failed. Output below:")
        print(result.stdout)
except Exception as e:
    print(f"[!] Error running OpenOCD: {e}")

print("[✓] JTAG Auto Interface Module Completed.")
