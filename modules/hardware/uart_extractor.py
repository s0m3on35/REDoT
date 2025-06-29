#!/usr/bin/env python3
import serial
import serial.tools.list_ports
import os
import time
import re

BAUD_RATES = [9600, 19200, 38400, 57600, 115200, 74880, 57600]
CREDENTIALS = [
    ("admin", "admin"),
    ("root", "root"),
    ("admin", "1234"),
    ("root", "toor"),
    ("user", "user"),
]
OUTPUT_DIR = "logs/uart"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fingerprint_protocol(output):
    lower = output.lower()
    if "login:" in lower or "password:" in lower:
        return "Shell / Login prompt"
    elif "uboot" in lower:
        return "Bootloader (U-Boot)"
    elif "telnet" in lower:
        return "Telnet Service"
    elif "busybox" in lower:
        return "BusyBox Shell"
    return "Unknown / Raw"

def try_credentials(ser):
    for username, password in CREDENTIALS:
        try:
            ser.write((username + "\n").encode())
            time.sleep(0.5)
            ser.write((password + "\n").encode())
            time.sleep(0.5)
            response = ser.read(200).decode(errors="ignore")
            if any(x in response.lower() for x in ["#", "$", ">"]):
                return (username, password, response)
        except Exception:
            continue
    return (None, None, "")

def scan_uart_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No UART ports found.")
        return

    for port in ports:
        print(f"[+] Scanning port: {port.device}")
        for baud in BAUD_RATES:
            try:
                with serial.Serial(port.device, baudrate=baud, timeout=2) as ser:
                    print(f"  Trying baud: {baud}")
                    ser.write(b"\n")
                    time.sleep(1)
                    output = ser.read(200).decode(errors="ignore")
                    if output.strip():
                        print(f"  >>> Output at {baud}: {output.strip()[:60]}...")
                        proto = fingerprint_protocol(output)
                        print(f"  [*] Detected protocol: {proto}")

                        user, pwd, shell = try_credentials(ser)
                        creds_used = f"Login attempt: {user}/{pwd}" if user else "No valid creds"
                        print(f"  [*] {creds_used}")

                        logname = f"{port.device.replace('/', '_')}_{baud}.log"
                        with open(os.path.join(OUTPUT_DIR, logname), "w") as f:
                            f.write(f"Port: {port.device}\nBaud: {baud}\nProtocol: {proto}\n")
                            f.write(f"{creds_used}\n\n")
                            f.write("Output:\n" + output + "\n\nShell:\n" + shell)
            except Exception as e:
                print(f"  [-] Error on {port.device} @ {baud}: {e}")

if __name__ == "__main__":
    print("=== REDOT UART Extractor ===")
    scan_uart_ports()
    print("[✓] UART scan complete.")
