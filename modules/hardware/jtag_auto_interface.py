#!/usr/bin/env python3
import subprocess
import time
import os
import re
import sys

# Paths to OpenOCD config directories
INTERFACE_DIR = "/usr/share/openocd/scripts/interface"
TARGET_DIR = "/usr/share/openocd/scripts/target"
OUTPUT_DIR = "logs/jtag"

# Known mappings for prioritized detection
INTERFACE_MAP = {
    "Olimex": "ftdi/olimex-arm-usb-tiny-h.cfg",
    "STMicroelectronics": "stlink.cfg",
    "FTDI": "ftdi/ft2232h_breakout.cfg",
    "SEGGER": "jlink.cfg",
    "Silicon Labs": "cmsis-dap.cfg"
}

TARGET_GUESS_LIST = [
    "stm32f1x.cfg",
    "stm32f4x.cfg",
    "nrf52.cfg",
    "esp32.cfg",
    "lpc176x.cfg",
    "at91sam7x.cfg"
]

def run_openocd(interface_cfg, target_cfg):
    print(f"[*] Testing Interface: {interface_cfg} | Target: {target_cfg}")
    cmd = [
        "openocd",
        "-f", os.path.join(INTERFACE_DIR, interface_cfg),
        "-f", os.path.join(TARGET_DIR, target_cfg),
        "-c", "init; scan_chain; exit"
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=10).decode()
        if "TAP" in output or "IRLength" in output:
            print("[+] Successful JTAG interface detected")
            return True
    except Exception:
        return False
    return False

def find_working_combo():
    for vendor, iface_cfg in INTERFACE_MAP.items():
        for tgt_cfg in TARGET_GUESS_LIST:
            if run_openocd(iface_cfg, tgt_cfg):
                return iface_cfg, tgt_cfg
    return None, None

def dump_flash(interface_cfg, target_cfg):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_file = os.path.join(OUTPUT_DIR, "jtag_flash_dump.bin")
    cmd = [
        "openocd",
        "-f", os.path.join(INTERFACE_DIR, interface_cfg),
        "-f", os.path.join(TARGET_DIR, target_cfg),
        "-c", f"init; halt; dump_image {out_file} 0x08000000 0x10000; exit"
    ]
    print(f"[+] Dumping flash memory to {out_file}")
    subprocess.call(cmd)

def install_as_service():
    print("[+] Creating systemd service for REDOT JTAG module...")
    service_path = "/etc/systemd/system/jtag_dump.service"
    script_path = os.path.abspath(__file__)
    service_content = f"""[Unit]
Description=REDOT JTAG Auto Interface Flash Dumper
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={os.path.dirname(script_path)}
ExecStart=/usr/bin/python3 {script_path}
StandardOutput=append:/opt/REDoT/logs/jtag/jtag_dump.log
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
    with open(service_path, "w") as f:
        f.write(service_content)
    os.system("systemctl daemon-reexec")
    os.system("systemctl enable jtag_dump.service")
    os.system("systemctl start jtag_dump.service")
    print(f"[✓] Service created and started: {service_path}")

def main():
    print("=== REDOT JTAG Auto Interface ===")
    print("Choose an option:")
    print("1. Run now")
    print("2. Install as persistent systemd service")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "2":
        install_as_service()
        return

    iface, target = find_working_combo()
    if not iface or not target:
        print("[-] No valid JTAG interface/target combination found.")
        return
    print(f"[+] Using interface: {iface}")
    print(f"[+] Using target: {target}")
    dump_flash(iface, target)
    print("[✓] Flash dump complete. Output saved in logs/jtag/")

if __name__ == "__main__":
    main()
