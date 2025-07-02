# modules/attacks/uart_command_injector.py

import serial
import argparse
import time
import json
import os
from datetime import datetime

LOG_PATH = "results/uart_command_log.json"
MITRE_TTP = "T1040"

def log_injection(entry):
    os.makedirs("results", exist_ok=True)
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def inject_uart(port, baud, command, delay=2):
    try:
        with serial.Serial(port, baudrate=baud, timeout=2) as ser:
            time.sleep(delay)
            ser.write(command.encode("utf-8") + b"\n")
            response = ser.read(128).decode("utf-8", errors="ignore")
            log_injection({
                "timestamp": datetime.utcnow().isoformat(),
                "port": port,
                "baud": baud,
                "command": command,
                "response": response,
                "ttp": MITRE_TTP
            })
            return response
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UART command injector (bootloader/firmware control)")
    parser.add_argument("--port", required=True, help="Serial port (e.g., /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    parser.add_argument("--command", required=True, help="Command to send")
    parser.add_argument("--delay", type=int, default=2, help="Delay before write (sec)")
    args = parser.parse_args()

    response = inject_uart(args.port, args.baud, args.command, args.delay)
    print("[UART RESPONSE]")
    print(response)
