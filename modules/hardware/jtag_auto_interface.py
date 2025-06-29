#!/usr/bin/env python3
import subprocess
import os
import re
import json
import hashlib
import datetime
import shutil
import sys

INTERFACE_DIR = "/usr/share/openocd/scripts/interface"
TARGET_DIR = "/usr/share/openocd/scripts/target"
OUTPUT_BASE = "logs/jtag"
OPENOCD_BIN = "openocd"

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

def check_openocd():
    try:
        subprocess.check_output([OPENOCD_BIN, '--version'], stderr=subprocess.STDOUT)
    except FileNotFoundError:
        print("[-] OpenOCD not found. Please install it.")
        sys.exit(1)

def hash_file(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def guess_flash_size(output):
    match = re.search(r"flash size = (\d+)kbytes", output.lower())
    return int(match.group(1)) * 1024 if match else 0x10000

def extract_chip_id(output):
    match = re.search(r"idcode:\s+0x([0-9a-fA-F]+)", output)
    return f"0x{match.group(1)}" if match else "Unknown"

def run_openocd(interface_cfg, target_cfg):
    cmd = [
        OPENOCD_BIN,
        "-f", os.path.join(INTERFACE_DIR, interface_cfg),
        "-f", os.path.join(TARGET_DIR, target_cfg),
        "-c", "init; scan_chain; exit"
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=15).decode()
        if "TAP" in output or "IRLength" in output:
            return True, output
    except Exception:
        return False, ""
    return False, ""

def find_working_combo():
    for vendor, iface_cfg in INTERFACE_MAP.items():
        for tgt_cfg in TARGET_GUESS_LIST:
            print(f"[*] Trying {iface_cfg} + {tgt_cfg}")
            success, output = run_openocd(iface_cfg, tgt_cfg)
            if success:
                print("[+] Found valid combination")
                return iface_cfg, tgt_cfg, output
    return None, None, ""

def dump_flash(interface_cfg, target_cfg, flash_size, output_dir):
    out_file = os.path.join(output_dir, "jtag_flash_dump.bin")
    log_file = os.path.join(output_dir, "openocd.log")
    cmd = [
        OPENOCD_BIN,
        "-f", os.path.join(INTERFACE_DIR, interface_cfg),
        "-f", os.path.join(TARGET_DIR, target_cfg),
        "-c", f"init; halt; dump_image {out_file} 0x08000000 {flash_size}; exit"
    ]
    with open(log_file, 'w') as logf:
        subprocess.call(cmd, stdout=logf, stderr=logf)
    return out_file, log_file

def generate_report(info, output_dir):
    with open(os.path.join(output_dir, "report.json"), "w") as f:
        json.dump(info, f, indent=2)

def log_agent_to_json(name, ip, chip_id):
    agent_file = "webgui/agents.json"
    agents = []
    if os.path.exists(agent_file):
        with open(agent_file, 'r') as f:
            agents = json.load(f)
    agents.append({"name": name, "ip": ip, "chip_id": chip_id})
    with open(agent_file, 'w') as f:
        json.dump(agents, f, indent=2)

def create_output_folder():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(OUTPUT_BASE, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def main():
    print("=== REDOT JTAG Auto Interface ===")
    check_openocd()

    iface, target, scan_output = find_working_combo()
    if not iface or not target:
        print("[-] No valid JTAG combo found.")
        return

    chip_id = extract_chip_id(scan_output)
    flash_size = guess_flash_size(scan_output) or 0x10000
    output_dir = create_output_folder()

    print(f"[+] Interface: {iface}")
    print(f"[+] Target: {target}")
    print(f"[+] Chip ID: {chip_id}")
    print(f"[+] Flash size guess: {flash_size} bytes")

    dump_path, log_path = dump_flash(iface, target, flash_size, output_dir)
    sha256 = hash_file(dump_path)

    generate_report({
        "interface": iface,
        "target": target,
        "chip_id": chip_id,
        "flash_size": flash_size,
        "dump_file": dump_path,
        "sha256": sha256,
        "log_file": log_path
    }, output_dir)

    log_agent_to_json("JTAG-Agent", "192.168.88.99", chip_id)
    print(f"[✓] Dumped to {dump_path}")
    print(f"[✓] Metadata saved. SHA256: {sha256}")

if __name__ == "__main__":
    main()
