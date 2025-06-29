#!/usr/bin/env python3
import os
import subprocess
import time
import json
import shutil

OPENOCD_CONFIG_DIR = "/usr/share/openocd/scripts"
INTERFACES_DIR = os.path.join(OPENOCD_CONFIG_DIR, "interface")
TARGETS_DIR = os.path.join(OPENOCD_CONFIG_DIR, "target")
DUMP_OUTPUT = "logs/jtag_flash_dump.bin"
ANALYSIS_OUTPUT = "logs/jtag_analysis.txt"
UPLOAD_PATH = "webgui/static/jtag_uploaded.bin"

def list_configs(directory):
    return [f for f in os.listdir(directory) if f.endswith(".cfg")]

def auto_detect_openocd(interface, target):
    print(f"[*] Trying interface {interface} with target {target}...")
    cmd = [
        "openocd",
        "-f", os.path.join(INTERFACES_DIR, interface),
        "-f", os.path.join(TARGETS_DIR, target),
        "-c", "init; scan_chain; shutdown"
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=15).decode()
        if "IRLength" in output and "TAP" in output:
            print(f"[+] Success: Detected TAP with interface {interface} and target {target}")
            return True
    except subprocess.CalledProcessError as e:
        return False
    except subprocess.TimeoutExpired:
        return False
    return False

def find_working_combo():
    interfaces = list_configs(INTERFACES_DIR)
    targets = list_configs(TARGETS_DIR)
    for iface in interfaces:
        for tgt in targets:
            if auto_detect_openocd(iface, tgt):
                return iface, tgt
    return None, None

def dump_flash(interface, target):
    print("[*] Dumping flash via OpenOCD...")
    cmd = [
        "openocd",
        "-f", os.path.join(INTERFACES_DIR, interface),
        "-f", os.path.join(TARGETS_DIR, target),
        "-c", "init; halt; dump_image {} 0x08000000 0x100000; shutdown".format(DUMP_OUTPUT)
    ]
    subprocess.run(cmd)

def analyze_binary():
    print("[*] Analyzing binary with binwalk and strings...")
    with open(ANALYSIS_OUTPUT, "w") as out:
        out.write("== Binwalk Output ==\n")
        try:
            binwalk_out = subprocess.check_output(["binwalk", DUMP_OUTPUT]).decode()
            out.write(binwalk_out)
        except Exception as e:
            out.write(f"Binwalk failed: {e}\n")

        out.write("\n== Strings Output ==\n")
        try:
            strings_out = subprocess.check_output(["strings", DUMP_OUTPUT]).decode()
            out.write(strings_out)
        except Exception as e:
            out.write(f"strings failed: {e}\n")

def upload_to_dashboard():
    os.makedirs(os.path.dirname(UPLOAD_PATH), exist_ok=True)
    shutil.copy(DUMP_OUTPUT, UPLOAD_PATH)
    print(f"[+] Uploaded dump to {UPLOAD_PATH} for REDoT dashboard access.")

def main():
    print("=== REDOT JTAG Auto Interface ===")
    iface, tgt = find_working_combo()
    if not iface or not tgt:
        print("[-] No valid JTAG interface/target combo detected.")
        return
    print(f"[+] Using Interface: {iface}, Target: {tgt}")
    dump_flash(iface, tgt)
    analyze_binary()
    upload_to_dashboard()
    print("[✓] JTAG operation complete.")

if __name__ == "__main__":
    main()
