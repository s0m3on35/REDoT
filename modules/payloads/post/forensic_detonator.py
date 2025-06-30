#!/usr/bin/env python3
# REDOT: forensic_detonator.py
# Anti-analysis trap: detects forensic analysis or sandbox environments and triggers countermeasures

import os
import time
import sys
import subprocess
import platform
import logging

LOG_DIR = "logs/forensic_detonator"
LOG_FILE = os.path.join(LOG_DIR, "detonator.log")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(filename=LOG_FILE,
                    format='[%(asctime)s] %(message)s',
                    level=logging.INFO,
                    datefmt='%H:%M:%S')

def log(msg):
    logging.info(msg)
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def check_debugger_presence():
    """
    Detect common debugging tools presence (Linux example: check processes)
    """
    try:
        out = subprocess.check_output(['ps', 'aux'], text=True)
        debuggers = ['gdb', 'strace', 'ltrace', 'dbg', 'ida', 'ollydbg', 'windbg']
        for dbg in debuggers:
            if dbg in out.lower():
                log(f"[DETECT] Debugger detected: {dbg}")
                return True
        return False
    except Exception:
        return False

def check_vm_environment():
    """
    Check for common VM environment indicators
    """
    try:
        dmi = subprocess.check_output(['cat', '/sys/class/dmi/id/product_name'], text=True).lower()
        vm_indicators = ['virtualbox', 'vmware', 'kvm', 'qemu', 'hyper-v', 'xen']
        for vm in vm_indicators:
            if vm in dmi:
                log(f"[DETECT] VM environment detected: {vm}")
                return True
        return False
    except Exception:
        return False

def check_sandbox_artifacts():
    """
    Check for sandbox-specific artifacts like files or registry keys
    """
    sandbox_files = [
        '/usr/bin/cuckoo',
        '/usr/bin/sandbox',
        '/usr/bin/sandboxie',
    ]
    for f in sandbox_files:
        if os.path.exists(f):
            log(f"[DETECT] Sandbox artifact found: {f}")
            return True
    return False

def wipe_logs():
    """
    Dangerous: wipes logs to remove evidence. Use carefully.
    """
    try:
        if os.path.isdir("logs"):
            for root, dirs, files in os.walk("logs"):
                for file in files:
                    path = os.path.join(root, file)
                    os.remove(path)
            log("[ACTION] Logs wiped successfully")
    except Exception as e:
        log(f"[ACTION] Failed to wipe logs: {e}")

def trigger_self_destruct():
    """
    Dangerous: Example destructive action - overwrite file or halt system.
    """
    log("[ACTION] Triggering self-destruct sequence!")
    # Overwrite this script file with random data as an example
    try:
        with open(sys.argv[0], "wb") as f:
            f.write(os.urandom(1024*10))
        log("[ACTION] Script file corrupted")
    except Exception as e:
        log(f"[ACTION] Failed self-destruct overwrite: {e}")

    # Optionally halt the system (commented out for safety)
    # subprocess.run(['shutdown', '-h', 'now'])

def main():
    print("=== REDOT Forensic Detonator ===")
    log("Starting forensic detection loop")

    while True:
        detected = False
        if check_debugger_presence():
            detected = True
        if check_vm_environment():
            detected = True
        if check_sandbox_artifacts():
            detected = True

        if detected:
            log("[ALERT] Forensic analysis detected! Triggering countermeasures.")
            wipe_logs()
            trigger_self_destruct()
            break

        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()
